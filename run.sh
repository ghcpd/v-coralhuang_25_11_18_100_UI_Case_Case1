#!/bin/bash
# run.sh - Start a simple demo server (optional)

echo "========================================="
echo "Starting demo server for plugin testing"
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

echo ""
echo "This script provides a minimal HTTP server for testing."
echo "The actual plugin testing is done via test.sh"
echo ""
echo "Starting HTTP server on port 3000..."
echo "Press Ctrl+C to stop"
echo ""

$PYTHON_CMD -m http.server 3000
