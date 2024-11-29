#!/bin/bash

# Change to the project directory
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

echo installing requirements
# Install the required packages
pip install -r requirements.txt > /dev/null

echo installation complete.

# Print the current working directory to confirm
pwd
