# Plugin Bug Fixes - Outpainting Script

This project contains a buggy Stable Diffusion WebUI plugin (`input.py`) and its fixed version (`fixed_plugin.py`), along with a comprehensive test suite and reproducible environment.

## Overview

The original `input.py` contains four intentional bugs:
1. **Bug 1**: CheckboxGroup type mismatch (returns indices but code checks for strings)
2. **Bug 2**: Radio returns strings but backend expects integer index
3. **Bug 3**: Empty direction selection allowed (silent no-op)
4. **Bug 4**: Script shown in txt2img mode but crashes

All bugs are fixed in `fixed_plugin.py`. See `BUG_FIXES.md` for detailed explanations.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Bash (for shell scripts)
- Docker (optional, for containerized testing)

### Setup

1. **Install dependencies:**
   ```bash
   ./setup.sh
   ```

   This will:
   - Create a Python virtual environment
   - Install required packages (Pillow, gradio)

2. **Activate virtual environment** (if not auto-activated):
   ```bash
   # Linux/Mac
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

### Running Tests

Run the automated test suite:
```bash
./test.sh
```

Or run directly with Python:
```bash
python3 test_plugin.py
```

The test suite will:
- Verify all four bugs are fixed
- Test that the fixed plugin works correctly
- Report pass/fail status for each test

### Running Server (Not Required)

The `run.sh` script is provided for consistency but does nothing for this plugin (no server needed):
```bash
./run.sh
```

## Docker Testing

Build and run the Docker container to test in an isolated environment:

```bash
# Build the image
docker build -t plugin-test .

# Run tests in container
docker run --rm plugin-test
```

The Dockerfile:
- Installs all dependencies
- Copies project files
- Runs the test suite automatically

## Project Structure

```
.
├── input.py              # Original buggy plugin (read-only)
├── fixed_plugin.py       # Fixed plugin with all bugs resolved
├── test_plugin.py        # Comprehensive test suite
├── modules/              # Mock SD WebUI modules for testing
│   ├── __init__.py
│   ├── scripts.py
│   ├── images.py
│   ├── devices.py
│   ├── processing.py
│   └── shared.py
├── setup.sh              # Dependency installation script
├── run.sh                # Server/harness script (no-op for this plugin)
├── test.sh               # Test execution script
├── Dockerfile            # Containerized testing
├── BUG_FIXES.md          # Detailed bug fix documentation
└── README.md             # This file
```

## Test Results

Expected output when running `./test.sh`:

```
============================================================
PLUGIN TEST SUITE
============================================================

=== Test 1: Direction Type Mismatch (Bug 1) ===
  Fixed version: PASSED - Correctly handles direction as strings

=== Test 2: Inpainting Fill Type Mismatch (Bug 2) ===
  Fixed version: PASSED - p.inpainting_fill is correctly 0 (int)

=== Test 3: Empty Direction Selection (Bug 3) ===
  Fixed version: PASSED - Correctly raises ValueError

=== Test 4: txt2img Mode Handling (Bug 4) ===
  Fixed version: PASSED - Correctly raises ValueError

=== Test 5: show() Method (Bug 4) ===
  Fixed version: Shows in txt2img=False, img2img=True (CORRECT)

=== Test 6: Fixed Plugin Basic Functionality ===
  Fixed version: PASSED - Basic functionality works correctly

============================================================
TEST RESULTS SUMMARY
============================================================
  PASS: Bug 1: Direction Type Mismatch
  PASS: Bug 2: Inpainting Fill Type Mismatch
  PASS: Bug 3: Empty Direction
  PASS: Bug 4: txt2img Mode
  PASS: show() Method
  PASS: Basic Functionality

Total: 6/6 tests passed

✓ All tests passed!
```

## Bug Fix Details

For detailed explanations of each bug and how it was fixed, see `BUG_FIXES.md`.

## Notes

- The original `input.py` is treated as read-only and should not be modified
- Mock modules in `modules/` simulate SD WebUI APIs for testing purposes
- Tests verify both that bugs exist in the original and are fixed in the new version
- All tests execute real code (no mocked results)

## Troubleshooting

**Issue**: `python3: command not found`
- **Solution**: Use `python` instead, or install Python 3

**Issue**: Permission denied when running scripts
- **Solution**: Make scripts executable: `chmod +x setup.sh test.sh run.sh`

**Issue**: Virtual environment not activating
- **Solution**: Manually activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)

**Issue**: Tests fail with import errors
- **Solution**: Ensure virtual environment is activated and dependencies are installed: `./setup.sh`

