"""Mock modules.processing for testing"""

class Processed:
    """Mock Processed result"""
    def __init__(self, p, images, seed, info):
        self.images = images
        self.seed = seed
        self.info = info


def process_images(p):
    """Mock process_images function"""
    from PIL import Image
    # Return a mock processed result
    result_image = Image.new("RGB", (p.width, p.height), color=(100, 150, 200))
    return Processed(p, [result_image], p.seed, "Mock processing info")
