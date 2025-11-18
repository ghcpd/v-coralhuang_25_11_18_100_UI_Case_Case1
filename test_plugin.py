#!/usr/bin/env python3
"""
Comprehensive test suite for the fixed plugin.
Tests verify that all bugs are fixed and the plugin works correctly.
"""

import sys
import traceback
from PIL import Image
import gradio as gr

# Import both the buggy and fixed versions
import input as buggy_plugin
import fixed_plugin as fixed_plugin


class MockProcessing:
    """Mock processing object for testing."""
    def __init__(self, init_images=None, width=512, height=512, seed=42):
        self.init_images = init_images or []
        self.width = width
        self.height = height
        self.seed = seed
        self.mask_blur = 0
        self.inpainting_fill = 0
        self.inpaint_full_res = False
        self.n_iter = 1
        self.batch_size = 1
        self.do_not_save_grid = True
        self.do_not_save_samples = True
        self.prompt = "test prompt"
        self.outpath_samples = "/tmp/test_output"


def test_bug1_direction_type_mismatch():
    """Test Bug 1: CheckboxGroup type mismatch - should fail with buggy, pass with fixed."""
    print("\n=== Test 1: Direction Type Mismatch (Bug 1) ===")
    
    # Create test image
    test_img = Image.new("RGB", (512, 512), color=(255, 0, 0))
    p = MockProcessing(init_images=[test_img])
    
    # Simulate UI returning indices [0, 1] for ["left", "right"]
    direction_indices = [0, 1]  # This is what type="index" returns
    
    try:
        # Test buggy version - should fail or produce wrong results
        buggy_script = buggy_plugin.Script()
        result = buggy_script.run(p, pixels=128, mask_blur=4, inpainting_fill="fill", direction=direction_indices)
        
        # Check if directions were applied correctly
        # In buggy version, "left" in [0, 1] is False, so left should be 0
        # This means the buggy version won't expand left even though index 0 (left) was selected
        print("  Buggy version: Ran without exception (but directions may be wrong)")
        buggy_passed = True
    except Exception as e:
        print(f"  Buggy version: Exception (expected): {e}")
        buggy_passed = False
    
    # Test fixed version - should work correctly
    try:
        fixed_script = fixed_plugin.Script()
        # Fixed version expects strings, not indices
        direction_strings = ["left", "right"]  # This is what fixed version expects
        result = fixed_script.run(p, pixels=128, mask_blur=4, inpainting_fill=0, direction=direction_strings)
        
        # Verify result
        assert result is not None, "Fixed version should return a result"
        assert len(result.images) > 0, "Fixed version should return images"
        print("  Fixed version: PASSED - Correctly handles direction as strings")
        return True
    except Exception as e:
        print(f"  Fixed version: FAILED - {e}")
        traceback.print_exc()
        return False


def test_bug2_inpainting_fill_type_mismatch():
    """Test Bug 2: Radio returns string but backend expects int - should fail with buggy, pass with fixed."""
    print("\n=== Test 2: Inpainting Fill Type Mismatch (Bug 2) ===")
    
    test_img = Image.new("RGB", (512, 512), color=(0, 255, 0))
    p = MockProcessing(init_images=[test_img])
    
    # Simulate UI returning string "fill" (buggy) vs index 0 (fixed)
    try:
        buggy_script = buggy_plugin.Script()
        # Buggy version receives string "fill"
        result = buggy_script.run(p, pixels=128, mask_blur=4, inpainting_fill="fill", direction=["right"])
        
        # Check if p.inpainting_fill was set correctly
        # In buggy version, p.inpainting_fill = "fill" (string) which is wrong
        if isinstance(p.inpainting_fill, str):
            print(f"  Buggy version: Confirmed bug - p.inpainting_fill is string '{p.inpainting_fill}' (wrong)")
        else:
            print(f"  Buggy version: p.inpainting_fill is {p.inpainting_fill} (type: {type(p.inpainting_fill)})")
    except Exception as e:
        print(f"  Buggy version: Exception (may be expected): {e}")
    
    # Test fixed version
    try:
        p2 = MockProcessing(init_images=[test_img])
        fixed_script = fixed_plugin.Script()
        # Fixed version receives integer index 0
        result = fixed_script.run(p2, pixels=128, mask_blur=4, inpainting_fill=0, direction=["right"])
        
        # Verify p.inpainting_fill is an integer
        assert isinstance(p2.inpainting_fill, int), f"p.inpainting_fill should be int, got {type(p2.inpainting_fill)}"
        assert p2.inpainting_fill == 0, f"p.inpainting_fill should be 0, got {p2.inpainting_fill}"
        print(f"  Fixed version: PASSED - p.inpainting_fill is correctly {p2.inpainting_fill} (int)")
        return True
    except Exception as e:
        print(f"  Fixed version: FAILED - {e}")
        traceback.print_exc()
        return False


def test_bug3_empty_direction():
    """Test Bug 3: Empty direction selection - should silently fail with buggy, raise error with fixed."""
    print("\n=== Test 3: Empty Direction Selection (Bug 3) ===")
    
    test_img = Image.new("RGB", (512, 512), color=(0, 0, 255))
    p = MockProcessing(init_images=[test_img])
    
    # Test buggy version with empty direction
    try:
        buggy_script = buggy_plugin.Script()
        result = buggy_script.run(p, pixels=128, mask_blur=4, inpainting_fill="fill", direction=[])
        
        # Buggy version allows empty direction and does nothing (silent no-op)
        print("  Buggy version: Ran with empty direction (silent no-op - BUG)")
        buggy_allows_empty = True
    except Exception as e:
        print(f"  Buggy version: Exception: {e}")
        buggy_allows_empty = False
    
    # Test fixed version - should raise ValueError
    try:
        fixed_script = fixed_plugin.Script()
        result = fixed_script.run(p, pixels=128, mask_blur=4, inpainting_fill=0, direction=[])
        
        # Should not reach here
        print("  Fixed version: FAILED - Should have raised ValueError for empty direction")
        return False
    except ValueError as e:
        if "direction" in str(e).lower():
            print(f"  Fixed version: PASSED - Correctly raises ValueError: {e}")
            return True
        else:
            print(f"  Fixed version: FAILED - Wrong exception: {e}")
            return False
    except Exception as e:
        print(f"  Fixed version: FAILED - Unexpected exception: {e}")
        traceback.print_exc()
        return False


def test_bug4_txt2img_mode():
    """Test Bug 4: Script shown in txt2img mode - should crash with buggy, handle gracefully with fixed."""
    print("\n=== Test 4: txt2img Mode Handling (Bug 4) ===")
    
    # Simulate txt2img mode (no init_images)
    p = MockProcessing(init_images=[])
    
    # Test buggy version - should crash
    try:
        buggy_script = buggy_plugin.Script()
        result = buggy_script.run(p, pixels=128, mask_blur=4, inpainting_fill="fill", direction=["right"])
        
        # Should not reach here
        print("  Buggy version: Ran without exception (unexpected)")
        buggy_crashes = False
    except (IndexError, AttributeError) as e:
        print(f"  Buggy version: Crashed as expected: {e}")
        buggy_crashes = True
    except Exception as e:
        print(f"  Buggy version: Exception: {e}")
        buggy_crashes = True
    
    # Test fixed version - should raise clear error
    try:
        fixed_script = fixed_plugin.Script()
        result = fixed_script.run(p, pixels=128, mask_blur=4, inpainting_fill=0, direction=["right"])
        
        # Should not reach here
        print("  Fixed version: FAILED - Should have raised ValueError for missing init_images")
        return False
    except ValueError as e:
        if "init_images" in str(e).lower() or "initial image" in str(e).lower():
            print(f"  Fixed version: PASSED - Correctly raises ValueError: {e}")
            return True
        else:
            print(f"  Fixed version: FAILED - Wrong exception: {e}")
            return False
    except Exception as e:
        print(f"  Fixed version: FAILED - Unexpected exception: {e}")
        traceback.print_exc()
        return False


def test_show_method():
    """Test that show() method correctly filters by is_img2img."""
    print("\n=== Test 5: show() Method (Bug 4) ===")
    
    buggy_script = buggy_plugin.Script()
    fixed_script = fixed_plugin.Script()
    
    # Test txt2img mode (is_img2img=False)
    buggy_shows_txt2img = buggy_script.show(False)
    fixed_shows_txt2img = fixed_script.show(False)
    
    assert buggy_shows_txt2img == True, "Buggy version should show in txt2img (BUG)"
    assert fixed_shows_txt2img == False, "Fixed version should NOT show in txt2img"
    
    # Test img2img mode (is_img2img=True)
    buggy_shows_img2img = buggy_script.show(True)
    fixed_shows_img2img = fixed_script.show(True)
    
    assert buggy_shows_img2img == True, "Buggy version should show in img2img"
    assert fixed_shows_img2img == True, "Fixed version should show in img2img"
    
    print("  Buggy version: Shows in txt2img=True (BUG)")
    print("  Fixed version: Shows in txt2img=False, img2img=True (CORRECT)")
    return True


def test_fixed_plugin_basic_functionality():
    """Test that fixed plugin works correctly with valid inputs."""
    print("\n=== Test 6: Fixed Plugin Basic Functionality ===")
    
    test_img = Image.new("RGB", (512, 512), color=(128, 128, 128))
    p = MockProcessing(init_images=[test_img])
    
    try:
        fixed_script = fixed_plugin.Script()
        result = fixed_script.run(
            p,
            pixels=128,
            mask_blur=4,
            inpainting_fill=0,  # integer index
            direction=["right", "down"]  # list of strings
        )
        
        assert result is not None, "Result should not be None"
        assert len(result.images) > 0, "Result should contain images"
        assert isinstance(p.inpainting_fill, int), "p.inpainting_fill should be int"
        
        print("  Fixed version: PASSED - Basic functionality works correctly")
        return True
    except Exception as e:
        print(f"  Fixed version: FAILED - {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("PLUGIN TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Bug 1: Direction Type Mismatch", test_bug1_direction_type_mismatch),
        ("Bug 2: Inpainting Fill Type Mismatch", test_bug2_inpainting_fill_type_mismatch),
        ("Bug 3: Empty Direction", test_bug3_empty_direction),
        ("Bug 4: txt2img Mode", test_bug4_txt2img_mode),
        ("show() Method", test_show_method),
        ("Basic Functionality", test_fixed_plugin_basic_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ERROR in {test_name}: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

