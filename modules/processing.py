class Processed:
    def __init__(self, p, images, seed, info):
        self.images = images
        self.seed = seed
        self.info = info


def process_images(p):
    return Processed(p, p.init_images, getattr(p, "seed", 0), "processed")
