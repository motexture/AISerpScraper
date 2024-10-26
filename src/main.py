import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QProgressBar, QLabel, QTextEdit, QSpinBox
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
from googlesearch import search
from ui.content import ContentPanel
import requests
from bs4 import BeautifulSoup
import time
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class ScrapeWorkerSignals(QObject):
    """Defines the signals available from a running search thread."""
    result = pyqtSignal(list)  # Signal to send the search results back
    finished = pyqtSignal()    # Signal when the search finishes
    keyword = pyqtSignal(str)  # Progress signal
    progress = pyqtSignal(int)  # Progress signal
    error = pyqtSignal(str)    # Signal to send error messages

class ScrapeWorker(QRunnable):
    """Search worker that runs in a separate thread."""
    def __init__(self, keywords_to_generate, num_results_per_keyword, description):
        super().__init__()
        self.keywords_to_generate = keywords_to_generate
        self.num_results_per_keyword = num_results_per_keyword
        self.description = description
        self.signals = ScrapeWorkerSignals()
        self.is_interrupted = False  # Flag to check if the worker is stopped

    def run(self):
        """Perform the search and send the results."""
        results = []

        # Perform the search
        try:
            for i in range(0, self.keywords_to_generate):
                if self.is_interrupted:
                    break  # Stop if the worker is interrupted
                # Generate keyword based on description
                keyword = main_window.get_keyword(self.description)
                if not keyword:
                    self.signals.error.emit("No keyword generated.")
                    break

                # Emit the keyword for progress purposes
                self.signals.keyword.emit(keyword)

                # Perform search and convert the generator to a list
                scrape_results = list(search(keyword, num_results=self.num_results_per_keyword))

                # Loop through each URL in the search results
                for url in scrape_results:
                    if self.is_interrupted:
                        break  # Stop if the worker is interrupted

                    # Get page info (title and meta description)
                    title, meta_description = self.get_page_info(url)
                    print(f"URL: {url}, Title: {title}, Description: {meta_description}")
                    results.append((url, title, meta_description, keyword))

                    time.sleep(0.1)  # Simulate progress delay
                
                # Emit progress
                progress = int(((i + 1) / self.keywords_to_generate) * 100)
                self.signals.progress.emit(progress)

                if self.is_interrupted:
                    break  # Stop if the worker is interrupted
        except Exception as e:
            self.signals.error.emit(f"Error occurred: {str(e)}")
            self.signals.result.emit([])  # Emit empty results on error
            return

        # Emit the results and finish signal
        self.signals.result.emit(results)
        self.signals.finished.emit()

    def stop(self):
        """Stop the worker."""
        self.is_interrupted = True

    def get_page_info(self, url):
        """Scrape the title and meta description from the webpage."""
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Get title
            title = soup.title.string if soup.title else "No Title Found"

            # Get meta description
            description_tag = soup.find('meta', attrs={'name': 'description'})
            if description_tag:
                meta_description = description_tag.get('content', 'No Description Found')
            else:
                meta_description = "No Description Found"

            return title, meta_description
        except Exception:
            return "No Title Found", "No Description Found"


class AISerpScraperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.threadpool = QThreadPool()  # Create a thread pool to manage threads
        self.current_worker = None  # To keep track of the running worker
        self.scraped_results = []  # Store results persistently

    def initUI(self):
        self.setWindowTitle('AI SERP SCRAPER')
        self.setGeometry(100, 100, 1000, 800)

        # Apply modern background style to the window
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(45, 45, 45, 255), stop:1 rgba(80, 80, 80, 255)
                );
                font-family: Arial;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 11px;
                font-weight: bold;  /* Make labels bold */
                color: white;        /* Set labels to white */
            }
            QSpinBox, QTextEdit {
                background-color: #333;
                color: white;  /* Set the text color to white */
                border: 1px solid #555;
                padding: 5px;
                font-size: 14px;
            }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 10px;
                background-color: #f3f3f3;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
                margin: 1px;
            }
        """)

        layout = QVBoxLayout(self)
        self.content_panel = ContentPanel()

        self.content_panel.stop_button.clicked.connect(self.stop_scrape)

        layout.addWidget(self.content_panel)
        
        self.setLayout(layout)

        model_id = "Qwen/Qwen2.5-0.5B-Instruct"
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            device_map="cpu", 
            trust_remote_code=True, 
        ).to("cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

        # Connect the search functionality
        self.content_panel.scrape_button.clicked.connect(self.scrape_content)

    def get_keyword(self, description):
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": (
                "Generate a single, natural-sounding medium/long-tail search query based on the provided description. "
                "The query should be phrased like how a user would type it into Google, using complete phrases, and should be between 8-12 tokens. "
                "Avoid lists of keywords or unnatural phrasing. "
                "Only respond with the query itself.\n\n"
                f"Description:\n\n{description}"
            )}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=16,
            temperature=0.7,
            do_sample=True
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].replace('"', '').replace("'", "").replace("-", " ").replace("_", " ")
        print(response)
        return response

    def scrape_content(self):
        """Run the search in a separate thread."""
        # Prevent spawning multiple workers
        if self.current_worker:
            return  # A worker is already running

        keywords_to_generate = self.content_panel.keyword_input.value()
        num_results_per_keyword = self.content_panel.result_input.value()
        description = self.content_panel.description_input.toPlainText()

        # Reset the error label
        self.content_panel.error_label.setText("")

        # Clear the current results before adding new ones
        self.content_panel.result_table.setRowCount(0)

        # Create a worker and move the search task to a separate thzread
        self.current_worker = ScrapeWorker(keywords_to_generate, num_results_per_keyword, description)
        self.current_worker.signals.result.connect(self.store_results)
        self.current_worker.signals.finished.connect(self.scrape_finished)
        self.current_worker.signals.keyword.connect(self.get_keyword)
        self.current_worker.signals.progress.connect(self.update_progress)
        self.current_worker.signals.error.connect(self.display_error)

        # Start the worker
        self.threadpool.start(self.current_worker)
        self.content_panel.progress_bar.setValue(0)
        self.content_panel.stop_button.setEnabled(True)
        self.content_panel.scrape_button.setEnabled(False)  # Disable the search button during the search

    def stop_scrape(self):
        """Stop the current worker."""
        if self.current_worker:
            self.current_worker.stop()
            self.content_panel.stop_button.setEnabled(False)  # Disable the stop button

    def scrape_finished(self):
        """Handle the search completion."""
        self.current_worker = None
        self.content_panel.progress_bar.setValue(100)
        self.content_panel.scrape_button.setEnabled(True)  # Re-enable the search button
        self.content_panel.stop_button.setEnabled(False)  # Disable the stop button

    def store_results(self, results):
        """Store results and display them."""
        self.scraped_results = results  # Store results in the persistent list
        self.content_panel.display_results(results)

    def update_progress(self, value):
        """Update the progress bar."""
        self.content_panel.progress_bar.setValue(value)

    def display_error(self, error_message):
        """Display an error message."""
        print(error_message)
        self.content_panel.error_label.setText(error_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = AISerpScraperApp()
    main_window.show()
    sys.exit(app.exec_())