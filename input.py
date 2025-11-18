import math

import modules.scripts as scripts
import gradio as gr
from PIL import Image, ImageDraw

from modules import images, devices
from modules.processing import Processed, process_images
from modules.shared import opts, state


class Script(scripts.Script):
    def title(self):
        return "Poor man's outpainting (buggy test case)"

    def show(self, is_img2img):
        """
        Bug 4:
        Always return True, so this script will appear in txt2img as well.
        In txt2img mode, p.init_images is usually empty and run() will break.
        """
        return True

    def ui(self, is_img2img):
        """
        Bug 4 (continued):
        Do not guard on is_img2img here, so UI is shown even when there is no init image.
        """

        pixels = gr.Slider(
            label="Pixels to expand",
            minimum=8,
            maximum=256,
            step=8,
            value=128,
            elem_id=self.elem_id("pixels"),
        )

        mask_blur = gr.Slider(
            label="Mask blur",
            minimum=0,
            maximum=64,
            step=1,
            value=4,
            elem_id=self.elem_id("mask_blur"),
        )

        # Bug 2:
        # Radio returns string values (e.g. "fill") instead of index.
        # Later we assign this directly to p.inpainting_fill, which expects an int index.
        inpainting_fill = gr.Radio(
            label="Masked content",
            choices=["fill", "original", "latent noise", "latent nothing"],
            value="fill",
            # type="index",  # removed on purpose to introduce a type mismatch
            elem_id=self.elem_id("inpainting_fill"),
        )

        # Bug 1 + Bug 3:
        # - type="index" makes the returned value a list of indices (e.g. [0, 1]),
        #   but run() still checks for strings like "left" in direction.
        # - value=[] allows an empty selection, which means "no direction selected"
        #   and leads to a "no-op" outpainting without any explicit error.
        direction = gr.CheckboxGroup(
            label="Outpainting direction",
            choices=["left", "right", "up", "down"],
            value=[],  # default to no direction selected (Bug 3)
            type="index",  # return indices instead of strings (Bug 1)
            elem_id=self.elem_id("direction"),
        )

        return [pixels, mask_blur, inpainting_fill, direction]

    def run(self, p, pixels, mask_blur, inpainting_fill, direction):
        """
        This run method contains multiple intentional UI / logic integration bugs:

        - Assumes p.init_images[0] always exists (Bug 4). In txt2img mode this will raise.
        - Uses inpainting_fill directly as p.inpainting_fill, even though it is a string (Bug 2).
        - Treats 'direction' as a list of strings ("left", "right", ...),
          but UI actually returns a list of indices (Bug 1).
        - Allows direction to be empty, resulting in no actual outpainting (Bug 3).
        """

        initial_seed = None
        initial_info = None

        # Bug 2: p.inpainting_fill expects an integer index,
        # but 'inpainting_fill' here is a string such as "fill".
        p.mask_blur = mask_blur * 2
        p.inpainting_fill = inpainting_fill
        p.inpaint_full_res = False

        # Bug 1 + 3:
        # direction is a list of indices (e.g. [0, 1]) or an empty list,
        # but we treat it as if it contained strings like "left", "right".
        left = pixels if "left" in direction else 0
        right = pixels if "right" in direction else 0
        up = pixels if "up" in direction else 0
        down = pixels if "down" in direction else 0

        # Bug 4:
        # In txt2img mode p.init_images is usually empty,
        # so this will raise IndexError: list index out of range.
        init_img = p.init_images[0]

        target_w = math.ceil((init_img.width + left + right) / 64) * 64
        target_h = math.ceil((init_img.height + up + down) / 64) * 64

        if left > 0:
            left = left * (target_w - init_img.width) // (left + right)
        if right > 0:
            right = target_w - init_img.width - left

        if up > 0:
            up = up * (target_h - init_img.height) // (up + down)
        if down > 0:
            down = target_h - init_img.height - up

        img = Image.new("RGB", (target_w, target_h))
        img.paste(init_img, (left, up))

        mask = Image.new("L", (img.width, img.height), "white")
        draw = ImageDraw.Draw(mask)
        draw.rectangle(
            (
                left + (mask_blur * 2 if left > 0 else 0),
                up + (mask_blur * 2 if up > 0 else 0),
                mask.width - right - (mask_blur * 2 if right > 0 else 0),
                mask.height - down - (mask_blur * 2 if down > 0 else 0),
            ),
            fill="black",
        )

        latent_mask = Image.new("L", (img.width, img.height), "white")
        latent_draw = ImageDraw.Draw(latent_mask)
        latent_draw.rectangle(
            (
                left + (mask_blur // 2 if left > 0 else 0),
                up + (mask_blur // 2 if up > 0 else 0),
                mask.width - right - (mask_blur // 2 if right > 0 else 0),
                mask.height - down - (mask_blur // 2 if down > 0 else 0),
            ),
            fill="black",
        )

        devices.torch_gc()

        grid = images.split_grid(img, tile_w=p.width, tile_h=p.height, overlap=pixels)
        grid_mask = images.split_grid(mask, tile_w=p.width, tile_h=p.height, overlap=pixels)
        grid_latent_mask = images.split_grid(latent_mask, tile_w=p.width, tile_h=p.height, overlap=pixels)

        p.n_iter = 1
        p.batch_size = 1
        p.do_not_save_grid = True
        p.do_not_save_samples = True

        work = []
        work_mask = []
        work_latent_mask = []
        work_results = []

        for (y, h, row), (_, _, row_mask), (_, _, row_latent_mask) in zip(
            grid.tiles, grid_mask.tiles, grid_latent_mask.tiles
        ):
            for tiledata, tiledata_mask, tiledata_latent_mask in zip(row, row_mask, row_latent_mask):
                x, w = tiledata[0:2]

                # This condition decides which tiles need processing.
                if (
                    x >= left
                    and x + w <= img.width - right
                    and y >= up
                    and y + h <= img.height - down
                ):
                    continue

                work.append(tiledata[2])
                work_mask.append(tiledata_mask[2])
                work_latent_mask.append(tiledata_latent_mask[2])

        batch_count = len(work)
        print(
            f"Poor man's outpainting (buggy) will process a total of {len(work)} images "
            f"tiled as {len(grid.tiles[0][2])}x{len(grid.tiles)}."
        )

        state.job_count = batch_count

        for i in range(batch_count):
            p.init_images = [work[i]]
            p.image_mask = work_mask[i]
            p.latent_mask = work_latent_mask[i]

            state.job = f"Batch {i + 1} out of {batch_count}"
            processed = process_images(p)

            if initial_seed is None:
                initial_seed = processed.seed
                initial_info = processed.info

            p.seed = processed.seed + 1
            work_results += processed.images

        image_index = 0
        for y, h, row in grid.tiles:
            for tiledata in row:
                x, w = tiledata[0:2]

                if (
                    x >= left
                    and x + w <= img.width - right
                    and y >= up
                    and y + h <= img.height - down
                ):
                    continue

                if image_index < len(work_results):
                    tiledata[2] = work_results[image_index]
                else:
                    tiledata[2] = Image.new("RGB", (p.width, p.height))
                image_index += 1

        combined_image = images.combine_grid(grid)

        if opts.samples_save:
            images.save_image(
                combined_image,
                p.outpath_samples,
                "",
                initial_seed,
                p.prompt,
                opts.samples_format,
                info=initial_info,
                p=p,
            )

        processed = Processed(p, [combined_image], initial_seed, initial_info)

        return processed
