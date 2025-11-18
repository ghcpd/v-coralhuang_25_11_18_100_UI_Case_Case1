from PIL import Image

from fixed_plugin import Script


class DummyPipeline:
    def __init__(self):
        self.width = 32
        self.height = 32
        self.prompt = "demo"
        self.outpath_samples = "samples"
        self.seed = 0
        self.init_images = [Image.new("RGB", (32, 32), "purple")]
        self.image_mask = None
        self.latent_mask = None


if __name__ == "__main__":
    script = Script()
    params = DummyPipeline()

    print("Running fixed outpainting script in isolation")
    processed = script.run(params, pixels=16, mask_blur=2, inpainting_fill=0, direction=["left"])
    result = processed.images[0]
    print(f"Produced image size: {result.size}")
