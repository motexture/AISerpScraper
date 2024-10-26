from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QPushButton, QLabel, QSpinBox, QTextEdit, QScrollArea, QProgressBar, QTableWidget, QTableWidgetItem, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
import csv

class ContentPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Main layout for the content panel
        layout = QVBoxLayout()

        keyword_layout = QHBoxLayout()

        self.keyword_label = QLabel('NUM OF KEYWORDS TO GENERATE:')
        self.keyword_label.setStyleSheet("color: white; font-weight: bold;")  # Set label color to white and bold

        self.keyword_input = QSpinBox(self)
        self.keyword_input.setMinimum(1)
        self.keyword_input.setMaximum(100)  # Max number of results
        self.keyword_input.setStyleSheet("""
            QSpinBox {
                color: white; 
                background-color: #333;  /* Dark background with white text */
                border: 1px solid #555;
                padding: 5px;
                font-size: 13px;
            }
            QSpinBox::up-button {
                background-color: #555;  /* Background color for up button */
            }
            QSpinBox::down-button {
                background-color: #555;  /* Background color for down button */
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
                border: none;
                color: white;  /* Set arrow color to white */
            }
        """)  # Set input field text and arrows to white

        keyword_layout.addWidget(self.keyword_label)
        keyword_layout.addWidget(self.keyword_input)

        # Number of Results Selector
        result_layout = QHBoxLayout()

        self.result_label = QLabel('NUM OF RESULTS PER KEYWORD:')
        self.result_label.setStyleSheet("color: white; font-weight: bold;")  # Set label color to white and bold

        self.result_input = QSpinBox(self)
        self.result_input.setMinimum(1)
        self.result_input.setMaximum(100)  # Max number of results
        self.result_input.setStyleSheet("""
            QSpinBox {
                color: white; 
                background-color: #333;  /* Dark background with white text */
                border: 1px solid #555;
                padding: 5px;
                font-size: 13px;
            }
            QSpinBox::up-button {
                background-color: #555;  /* Background color for up button */
            }
            QSpinBox::down-button {
                background-color: #555;  /* Background color for down button */
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
                border: none;
                color: white;  /* Set arrow color to white */
            }
        """)  # Set input field text and arrows to white

        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.result_input)

        # "What type of websites would you like to scrape" Field (multiline)
        description_layout = QHBoxLayout()
        self.description_label = QLabel('DESCRIBE WHAT TYPE OF WEBSITES TO SCRAPE:')
        self.description_label.setStyleSheet("color: white; font-weight: bold;")  # Set label color to white and bold

        self.description_input = QTextEdit(self)
        self.description_input.setPlaceholderText("Enter here a detailed description about what type of websites you'd like to search")
        self.description_input.setText(
            "I'm looking for websites focused on fantasy gaming specifically for PC players. "
            "These sites should cover a range of topics, including in-depth game reviews, strategy guides, "
            "character builds, and tips for popular fantasy games like The Witcher, Skyrim, and Final Fantasy. "
            "I’m also interested in websites that feature news updates on upcoming fantasy game releases, new mods, "
            "and expansion packs. Ideally, the sites would include forums or community sections where players can discuss "
            "game tactics, share gameplay experiences, and connect with other fans. Additionally, any websites that offer "
            "downloadable content or mods for fantasy games on PC would be useful. I’d prefer English-language websites "
            "that are frequently updated with the latest information."
        )
        self.description_input.setFixedHeight(80)  # Set the height to be less
        self.description_input.setStyleSheet("color: white; background-color: #333;")  # Set input field text to white
        description_layout.addWidget(self.description_label)
        description_layout.addWidget(self.description_input)
        self.description_label.setStyleSheet("padding-right: 20px;")  # Set label color to white and bold

        # Search Button
        self.scrape_button = QPushButton('SCRAPE')
        self.scrape_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* Initial background color */
                color: white;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;  /* Hover color */
            }
            QPushButton:pressed {
                background-color: #3d8c40;  /* Darker green when pressed */
            }
            QPushButton:disabled {
                background-color: grey;  /* Disabled state color */
                color: darkgrey;         /* Text color for disabled state */
            }
        """)

        # Copy URLs Button
        self.copy_button = QPushButton('COPY URLS')
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* Initial background color */
                color: white;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;  /* Hover color */
            }
            QPushButton:pressed {
                background-color: #3d8c40;  /* Darker green when pressed */
            }
        """)
        self.copy_button.clicked.connect(self.copy_urls_to_clipboard)

        # Export to CSV Button
        self.export_button = QPushButton('EXPORT TO CSV')
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* Initial background color */
                color: white;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;  /* Hover color */
            }
            QPushButton:pressed {
                background-color: #3d8c40;  /* Darker green when pressed */
            }
        """)
        self.export_button.clicked.connect(self.export_to_csv)

        # Export Selected to CSV Button
        self.export_selected_button = QPushButton('EXPORT SELECTED TO CSV')
        self.export_selected_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* Initial background color */
                color: white;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;  /* Hover color */
            }
            QPushButton:pressed {
                background-color: #3d8c40;  /* Darker green when pressed */
            }
        """)
        self.export_selected_button.clicked.connect(self.export_selected_to_csv)

        # Search Results Table with 4 columns (URL, Title, Description, keyword)
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["URL", "TITLE", "DESCRIPTION", "KEYWORD"])

        # Make all columns even in width
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Make all columns take equal space

        self.result_table.setSelectionBehavior(self.result_table.SelectRows)  # Allow selecting rows
        self.result_table.setSelectionMode(self.result_table.MultiSelection)  # Enable multi-row selection
        self.result_table.setStyleSheet("color: white; font-weight: bold; font-size: 11px; background-color: #222;")  # Set table text to white

        # Scrollable Result Area
        self.result_area = QScrollArea(self)
        self.result_area.setWidget(self.result_table)
        self.result_area.setWidgetResizable(True)

        # Add circular progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # Hide text for circular progress bar
        
        # Add stop button
        self.stop_button = QPushButton('STOP', self)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;  /* Initial background color */
                color: white;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff8c00;  /* Hover color */
            }
            QPushButton:pressed {
                background-color: red;  /* Darker green when pressed */
            }
            QPushButton:disabled {
                background-color: grey;  /* Disabled state color */
                color: darkgrey;         /* Text color for disabled state */
            }
        """)
        self.stop_button.setEnabled(False)  # Disable initially

        # Add error label
        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        self.error_label.setText("")  # Initially empty
        self.error_label.setWordWrap(True)

        # Add all components to the main layout
        layout.addLayout(keyword_layout)
        layout.addLayout(result_layout)
        layout.addLayout(description_layout)
        layout.addWidget(self.scrape_button)
        layout.addWidget(self.copy_button)  # Add the Copy URLs button
        layout.addWidget(self.export_button)  # Add the Export to CSV button
        layout.addWidget(self.export_selected_button)  # Add the Export Selected to CSV button
        layout.addWidget(self.result_area)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.stop_button)  # Add the Export Selected to CSV button
        layout.addWidget(self.error_label)  # Add the error label below progress bar

        # Set the layout for the content panel
        self.setLayout(layout)

    def display_results(self, results):
        """Display the scraped results in the table."""
        self.result_table.setRowCount(len(results))
        for row, (url, title, description, keyword) in enumerate(results):
            self.result_table.setItem(row, 0, QTableWidgetItem(url))
            self.result_table.setItem(row, 1, QTableWidgetItem(title))
            self.result_table.setItem(row, 2, QTableWidgetItem(description))
            self.result_table.setItem(row, 3, QTableWidgetItem(keyword))

    def copy_urls_to_clipboard(self):
        """Copy all URLs from the search results to the clipboard."""
        urls = []
        for row in range(self.result_table.rowCount()):
            url_item = self.result_table.item(row, 0)
            if url_item:
                urls.append(url_item.text())

        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(urls))  # Copy all URLs to the clipboard, separated by newlines

    def export_to_csv(self):
        """Export the table data to a CSV file."""
        # Open a file dialog to save the file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)", options=options)

        if file_name:
            # Append .csv if not present
            if not file_name.endswith(".csv"):
                file_name += ".csv"

            # Write the data to the CSV file
            with open(file_name, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write the header row
                writer.writerow(["URL", "TITLE", "DESCRIPTION", "KEYWORD"])
                
                # Write the rows from the table
                for row in range(self.result_table.rowCount()):
                    url_item = self.result_table.item(row, 0)
                    title_item = self.result_table.item(row, 1)
                    description_item = self.result_table.item(row, 2)
                    keyword_item = self.result_table.item(row, 3)

                    # Write the row data to the CSV file
                    writer.writerow([
                        url_item.text() if url_item else "",
                        title_item.text() if title_item else "",
                        description_item.text() if description_item else "",
                        keyword_item.text() if keyword_item else ""
                    ])

    def export_selected_to_csv(self):
        """Export the selected rows to a CSV file."""
        selected_rows = self.result_table.selectionModel().selectedRows()

        if not selected_rows:
            return  # Exit if no rows are selected

        # Open a file dialog to save the file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)", options=options)

        if file_name:
            # Append .csv if not present
            if not file_name.endswith(".csv"):
                file_name += ".csv"

            # Write the selected data to the CSV file
            with open(file_name, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write the header row
                writer.writerow(["URL", "TITLE", "DESCRIPTION", "KEYWORD"])
                
                # Write the selected rows
                for index in selected_rows:
                    row = index.row()
                    url_item = self.result_table.item(row, 0)
                    title_item = self.result_table.item(row, 1)
                    description_item = self.result_table.item(row, 2)
                    keyword_item = self.result_table.item(row, 3)

                    # Write the row data to the CSV file
                    writer.writerow([
                        url_item.text() if url_item else "",
                        title_item.text() if title_item else "",
                        description_item.text() if description_item else "",
                        keyword_item.text() if keyword_item else ""
                    ])
