"""
Mock modules.processing for testing purposes.
"""


class Processed:
    """Mock Processed class."""
    def __init__(self, p, images, seed, info):
        self.p = p
        self.images = images
        self.seed = seed
        self.info = info


def process_images(p):
    """
    Mock process_images function.
    Returns a Processed object with mock results.
    """
    from PIL import Image
    
    # Create a mock processed image
    if p.init_images and len(p.init_images) > 0:
        # Return the input image as-is for testing
        result_img = p.init_images[0].copy()
    else:
        result_img = Image.new("RGB", (p.width, p.height), color=(128, 128, 128))
    
    seed = getattr(p, 'seed', 42)
    info = "Mock processing info"
    
    return Processed(p, [result_img], seed, info)

