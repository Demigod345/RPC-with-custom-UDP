#!/bin/bash

echo "Setting up UDP RPC System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
pip install PyQt6

# Create login_data.txt if it doesn't exist
if [ ! -f login_data.txt ]; then
    echo "Creating login database file..."
    touch login_data.txt
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "Creating .gitignore..."
    echo "venv/" > .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
    echo "login_data.txt" >> .gitignore
fi

echo "Setup completed successfully!"
echo "To start the system:"
echo "1. Start the server: python3 server_frontend.py"
echo "2. Start the client: python3 client_frontend.py"
