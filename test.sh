#!/bin/bash
# Test script to run automated tests

set -e

echo "Running plugin tests..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
fi

# Check if Python is available
python3 --version || python --version || { echo "Error: Python is required"; exit 1; }

# Run the test suite
echo "Executing test suite..."
python3 test_plugin.py || python test_plugin.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✓ All tests passed!"
else
    echo ""
    echo "✗ Some tests failed (exit code: $exit_code)"
fi

exit $exit_code

