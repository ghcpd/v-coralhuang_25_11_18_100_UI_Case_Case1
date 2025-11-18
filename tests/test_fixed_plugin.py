from PIL import Image
import pytest

from fixed_plugin import (
    Script,
    compute_direction_offsets,
    ensure_fill_index,
    normalize_direction_input,
)
from modules.shared import opts, state


class DummyPipeline:
    def __init__(self):
        self.width = 32
        self.height = 32
        self.init_images = [Image.new("RGB", (32, 32), "blue")]
        self.seed = 1
        self.prompt = "test"
        self.outpath_samples = "samples"
        self.image_mask = None
        self.latent_mask = None


def test_normalize_direction_handles_mixed_inputs():
    normalized = normalize_direction_input([0, "left", "right", 2])
    assert normalized == ("left", "right", "up")

    normalized_single = normalize_direction_input("down")
    assert normalized_single == ("down",)


def test_direction_requires_selection():
    with pytest.raises(ValueError):
        compute_direction_offsets([], 16)


def test_ensure_fill_index_accepts_values():
    assert ensure_fill_index(2) == 2
    assert ensure_fill_index("Latent Noise") == 2

    with pytest.raises(ValueError):
        ensure_fill_index("invalid")


def test_script_run_produces_expected_image():
    opts.samples_save = False
    state.job_count = 0

    script = Script()
    dummy = DummyPipeline()

    processed = script.run(dummy, pixels=16, mask_blur=2, inpainting_fill=0, direction=["left"])

    assert processed.images
    assert processed.images[0].size == (64, 64)
    assert state.job_count == 1
