#!/bin/bash
# test.sh - Run the automated test suite

echo "========================================="
echo "Running Plugin Test Suite"
echo "========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed."
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

echo "Using Python: $($PYTHON_CMD --version)"
echo ""

# Check if required packages are installed
echo "Checking dependencies..."
if ! $PYTHON_CMD -c "import PIL" 2>/dev/null; then
    echo "ERROR: Pillow is not installed. Run ./setup.sh first."
    exit 1
fi

if ! $PYTHON_CMD -c "import gradio" 2>/dev/null; then
    echo "ERROR: Gradio is not installed. Run ./setup.sh first."
    exit 1
fi

echo "✓ All dependencies found"
echo ""

# Run the test suite
echo "========================================="
echo "Executing tests..."
echo "========================================="
echo ""

$PYTHON_CMD test_plugin.py

TEST_EXIT_CODE=$?

echo ""
echo "========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
    echo "========================================="
    exit 0
else
    echo "✗ TESTS FAILED"
    echo "========================================="
    exit 1
fi
