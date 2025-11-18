#!/bin/bash
# Setup script to install all required dependencies

set -e

echo "Setting up plugin testing environment..."

# Check Python version
python3 --version || { echo "Error: Python 3 is required"; exit 1; }

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
pip install Pillow gradio

echo ""
echo "Setup complete!"
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate  (Linux/Mac)"
echo "  venv\\Scripts\\activate  (Windows)"

