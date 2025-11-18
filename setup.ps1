# setup.ps1 - Install all required dependencies for Windows

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setting up environment for plugin testing" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Using Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed. Please install Python 3.7+ first." -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null

# Install required packages
Write-Host ""
Write-Host "Installing required packages..." -ForegroundColor Yellow
python -m pip install Pillow gradio

# Verify installations
Write-Host ""
Write-Host "Verifying installations..." -ForegroundColor Yellow
python -c "import PIL; print(f'✓ Pillow {PIL.__version__} installed')"
python -c "import gradio; print(f'✓ Gradio {gradio.__version__} installed')"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "You can now run:"
Write-Host "  .\test.ps1    - Run the test suite"
Write-Host "  .\run.ps1     - Start the demo server (optional)"
