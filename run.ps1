# run.ps1 - Start a simple demo server (optional)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Starting demo server for plugin testing" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Using Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "This script provides a minimal HTTP server for testing."
Write-Host "The actual plugin testing is done via test.ps1"
Write-Host ""
Write-Host "Starting HTTP server on port 3000..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop"
Write-Host ""

python -m http.server 3000
