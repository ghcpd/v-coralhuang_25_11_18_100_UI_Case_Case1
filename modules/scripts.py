class Script:
    def title(self):
        raise NotImplementedError()

    def show(self, is_img2img):
        return bool(is_img2img)

    def ui(self, is_img2img):
        raise NotImplementedError()

    def run(self, p, *args, **kwargs):
        raise NotImplementedError()

    def elem_id(self, suffix: str) -> str:
        return suffix
