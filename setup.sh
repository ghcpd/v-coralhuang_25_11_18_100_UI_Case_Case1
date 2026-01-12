#!/bin/bash
# setup.sh - Install all required dependencies

echo "========================================="
echo "Setting up environment for plugin testing"
echo "========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
else
    PYTHON_CMD=python
    PIP_CMD=pip
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Upgrade pip
echo ""
echo "Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip

# Install required packages
echo ""
echo "Installing required packages..."
$PIP_CMD install Pillow gradio

# Verify installations
echo ""
echo "Verifying installations..."
$PYTHON_CMD -c "import PIL; print(f'✓ Pillow {PIL.__version__} installed')"
$PYTHON_CMD -c "import gradio; print(f'✓ Gradio {gradio.__version__} installed')"

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo "You can now run:"
echo "  ./test.sh    - Run the test suite"
echo "  ./run.sh     - Start the demo server (optional)"
