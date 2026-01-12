# Quick Start Instructions

## For Reviewers/Testers

### Option 1: Run Tests Locally (Fastest)

**Windows:**
```powershell
# In PowerShell terminal
cd c:\Bug_Bash\25_11_18\v-coralhuang_25_11_18_case1
python -m pip install Pillow
python test_plugin.py
```

**Linux/Mac:**
```bash
cd /path/to/v-coralhuang_25_11_18_case1
chmod +x setup.sh test.sh
./setup.sh
./test.sh
```

### Option 2: Run Tests in Docker (Most Reproducible)

```bash
# Build the container
docker build -t plugin-tester .

# Run the tests
docker run plugin-tester
```

### Expected Output

You should see:
```
test_bug1_direction_type_mismatch ... ok
test_bug2_inpainting_fill_string_instead_of_int ... ok
test_bug3_empty_direction_allowed ... ok
test_bug4_crashes_in_txt2img_mode ... ok
test_bug4_show_returns_true_for_txt2img ... ok
test_all_inpainting_fill_options ... ok
test_fix1_direction_accepts_strings ... ok
test_fix2_inpainting_fill_is_integer ... ok
test_fix3_empty_direction_raises_error ... ok
test_fix4_show_returns_false_for_txt2img ... ok
test_fix4_validates_init_images ... ok
test_partial_directions ... ok
test_successful_run_with_valid_inputs ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.06s

OK
```

## What Gets Tested

### Bugs Verified in `input.py` (5 tests)
1. ✓ CheckboxGroup returns indices instead of strings
2. ✓ Radio returns string instead of integer index
3. ✓ Empty direction selection allowed (silent no-op)
4. ✓ Script shows in txt2img mode (causes crash)
5. ✓ No validation of init_images

### Fixes Verified in `fixed_plugin.py` (8 tests)
1. ✓ Direction selection works with strings
2. ✓ Inpainting fill uses integer indices
3. ✓ Empty direction raises validation error
4. ✓ Script only shows in img2img mode
5. ✓ Init images are validated
6. ✓ All inpainting fill options work
7. ✓ Partial direction selections work
8. ✓ Full integration test passes

## Key Files

- **`input.py`** - Original buggy code (DO NOT MODIFY)
- **`fixed_plugin.py`** - Fixed version with all bugs resolved
- **`test_plugin.py`** - Test suite (13 automated tests)
- **`README.md`** - Full documentation
- **`BUG_FIXES_SUMMARY.md`** - Executive summary of fixes

## Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'PIL'`  
**Solution:** Run `python -m pip install Pillow`

**Problem:** PowerShell script execution error  
**Solution:** Run `python test_plugin.py` directly

**Problem:** Docker not found  
**Solution:** Install Docker Desktop or use Option 1

## Time Required

- **Setup:** < 2 minutes
- **Test execution:** < 5 seconds
- **Total:** < 3 minutes to verify everything works

## Success Criteria

✅ All 13 tests pass  
✅ No errors or exceptions  
✅ Output shows "OK" at the end

## Questions?

See `README.md` for comprehensive documentation including:
- Detailed bug analysis
- Design decisions
- File-by-file changes
- Architecture overview
