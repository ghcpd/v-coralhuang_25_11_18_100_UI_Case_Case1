# Plugin Bug Fixes and Testing Environment

## Overview
This project contains a buggy Stable Diffusion WebUI-style outpainting script (`input.py`) and a fixed version (`fixed_plugin.py`), along with comprehensive tests and a Docker environment for verification.

## Bugs Identified and Fixed

### Bug 1: CheckboxGroup Type Mismatch
**Problem:** In `input.py`, the `direction` CheckboxGroup uses `type="index"`, which returns a list of indices (e.g., `[0, 1, 2, 3]`). However, the `run()` method checks for string values like `"left" in direction`, causing all direction checks to fail silently.

**Impact:** No outpainting occurs in any direction because the string checks never match the integer indices.

**Fix:** In `fixed_plugin.py`, removed `type="index"` from the CheckboxGroup so it returns string values `["left", "right", "up", "down"]` that match the code checks.

### Bug 2: Radio Returns String Instead of Integer
**Problem:** In `input.py`, the `inpainting_fill` Radio component doesn't use `type="index"`, so it returns string values like `"fill"`, `"original"`, etc. These strings are assigned directly to `p.inpainting_fill`, which expects an integer index (0-3).

**Impact:** Type mismatch causes incorrect inpainting behavior or potential errors when the value is used by the underlying system.

**Fix:** In `fixed_plugin.py`, added `type="index"` to the Radio component so it returns integer indices (0, 1, 2, 3) instead of string values.

### Bug 3: Empty Direction Selection Allowed
**Problem:** In `input.py`, the `direction` CheckboxGroup has `value=[]` as default, allowing users to select no directions. The script runs without error but does nothing (silent no-op).

**Impact:** Confusing user experience - the script appears to work but produces no visible changes.

**Fix:** In `fixed_plugin.py`:
- Changed default value to `["left", "right", "up", "down"]` to encourage meaningful defaults
- Added validation in `run()` to raise a `ValueError` if no direction is selected

### Bug 4: Script Shown in txt2img Mode
**Problem:** In `input.py`, the `show()` method always returns `True`, making the script appear in txt2img mode. In txt2img mode, `p.init_images` is empty, causing `p.init_images[0]` to raise an `IndexError`.

**Impact:** Application crash when users try to use the script in txt2img mode.

**Fix:** In `fixed_plugin.py`:
- Modified `show()` to return `is_img2img`, restricting the script to img2img mode only
- Added defensive validation in `run()` to check for empty `init_images` and raise a clear error message

### Bonus Fix: Rectangle Bounds Validation
**Additional Issue Discovered:** When small images are used with large mask blur values, the rectangle coordinates can become invalid (x1 < x0 or y1 < y0), causing PIL to raise a `ValueError`.

**Fix:** Added bounds checking before drawing rectangles to ensure valid coordinates.

## Project Structure

```
.
├── input.py                  # Original buggy plugin (READ-ONLY)
├── fixed_plugin.py          # Fixed version with all bugs resolved
├── test_plugin.py           # Comprehensive test suite
├── modules/                 # Mock SD WebUI modules for testing
│   ├── __init__.py
│   ├── scripts.py
│   ├── processing.py
│   ├── shared.py
│   ├── devices.py
│   └── images.py
├── gradio.py               # Mock Gradio for testing
├── setup.sh / setup.ps1    # Dependency installation scripts
├── run.sh / run.ps1        # Optional demo server scripts
├── test.sh / test.ps1      # Test execution scripts
├── Dockerfile              # Container image for testing
└── README.md               # This file
```

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip
- Docker (optional, for containerized testing)

### Running Tests Locally

#### On Linux/Mac:
```bash
# Install dependencies
chmod +x setup.sh
./setup.sh

# Run tests
chmod +x test.sh
./test.sh
```

#### On Windows (PowerShell):
```powershell
# Install dependencies (if execution policy allows)
.\setup.ps1

# Or install manually:
python -m pip install Pillow

# Run tests
python test_plugin.py
```

### Using Docker

Build and run tests in a container:

```bash
# Build the Docker image
docker build -t plugin-tester .

# Run the tests
docker run plugin-tester

# Or run interactively
docker run -it plugin-tester /bin/bash
```

## Test Suite

The test suite (`test_plugin.py`) contains 13 tests divided into two categories:

### Tests for Buggy Plugin (5 tests)
These tests verify that the bugs exist in `input.py`:
- `test_bug4_show_returns_true_for_txt2img` - Confirms Bug 4 (show always returns True)
- `test_bug4_crashes_in_txt2img_mode` - Confirms Bug 4 (IndexError crash)
- `test_bug1_direction_type_mismatch` - Confirms Bug 1 (direction type mismatch)
- `test_bug2_inpainting_fill_string_instead_of_int` - Confirms Bug 2 (string instead of int)
- `test_bug3_empty_direction_allowed` - Confirms Bug 3 (empty direction allowed)

### Tests for Fixed Plugin (8 tests)
These tests verify that all bugs are fixed in `fixed_plugin.py`:
- `test_fix4_show_returns_false_for_txt2img` - Verifies show() works correctly
- `test_fix4_validates_init_images` - Verifies proper validation
- `test_fix1_direction_accepts_strings` - Verifies direction type is correct
- `test_fix2_inpainting_fill_is_integer` - Verifies inpainting_fill is integer
- `test_fix3_empty_direction_raises_error` - Verifies empty direction validation
- `test_successful_run_with_valid_inputs` - Integration test with valid inputs
- `test_partial_directions` - Tests partial direction selections
- `test_all_inpainting_fill_options` - Tests all inpainting fill options

### Test Results

When all tests pass, you'll see:
```
----------------------------------------------------------------------
Ran 13 tests in X.XXXs

OK
```

## Optional: Demo Server

The `run.sh` / `run.ps1` scripts start a simple HTTP server on port 3000 for demonstration purposes. This is not required for testing.

```bash
# Linux/Mac
./run.sh

# Windows
.\run.ps1

# Or manually
python -m http.server 3000
```

## Design Decisions

1. **Separate Fixed File:** Instead of modifying `input.py`, I created `fixed_plugin.py` to preserve the original buggy code for comparison and testing.

2. **Mock Modules:** Created lightweight mock implementations of SD WebUI modules to enable testing without requiring the full Stable Diffusion WebUI installation.

3. **Comprehensive Tests:** Tests verify both that bugs exist in the original and that they're fixed in the corrected version, providing confidence in the fixes.

4. **Cross-Platform Scripts:** Provided both shell scripts (.sh) and PowerShell scripts (.ps1) for compatibility.

5. **Docker Support:** Containerized environment ensures reproducible testing across different systems.

6. **Defensive Programming:** Added validation and bounds checking beyond fixing the identified bugs to improve robustness.

## File-by-File Changes

### `fixed_plugin.py`
- Line 19-22: Fixed `show()` to return `is_img2img` instead of `True`
- Line 45-46: Added `type="index"` to Radio component
- Line 56-57: Changed CheckboxGroup default to all directions, removed `type="index"`
- Line 71-80: Added validation for empty direction and empty init_images
- Line 92-110: Added bounds validation for rectangle drawing (bonus fix)

## Verification Steps

1. **Install dependencies:** Run `setup.sh` or install Pillow manually
2. **Run tests:** Execute `test.sh` or `python test_plugin.py`
3. **Verify Docker:** Build and run the Docker image
4. **Check results:** All 13 tests should pass

## Troubleshooting

**Issue:** Tests fail with `ModuleNotFoundError: No module named 'PIL'`  
**Solution:** Run `python -m pip install Pillow`

**Issue:** PowerShell execution policy error  
**Solution:** Run `python test_plugin.py` directly instead of using .ps1 scripts

**Issue:** Docker build fails  
**Solution:** Ensure Docker is installed and running, check internet connectivity

## Conclusion

This project demonstrates:
- Systematic bug identification and analysis
- Creating reproducible test environments
- Comprehensive testing of both buggy and fixed code
- Cross-platform compatibility
- Docker containerization for testing
- Defensive programming practices

All bugs have been successfully fixed and verified through automated testing.
