#!/bin/bash

# Create env and activate it
python3 -m venv myenv
source myenv/bin/activate

# Install other dependencies
pip install -r requirements.txt

# Install PyTorch with the specified index URL
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install accelerate