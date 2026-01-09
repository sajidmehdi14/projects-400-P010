#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Setup complete. Virtual environment activated."
echo "Run the API with: uvicorn app.main:app --reload"
