# test.ps1 - Run the automated test suite

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Running Plugin Test Suite" -ForegroundColor Cyan
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

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow

$pillowCheck = python -c "import PIL" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Pillow is not installed. Run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

$gradioCheck = python -c "import gradio" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Gradio is not installed. Run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "✓ All dependencies found" -ForegroundColor Green
Write-Host ""

# Run the test suite
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Executing tests..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

python test_plugin.py

$testExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
if ($testExitCode -eq 0) {
    Write-Host "✓ ALL TESTS PASSED" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "✗ TESTS FAILED" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Cyan
    exit 1
}
