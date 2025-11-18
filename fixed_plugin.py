import math

import modules.scripts as scripts
import gradio as gr
from PIL import Image, ImageDraw

from modules import images, devices
from modules.processing import Processed, process_images
from modules.shared import opts, state


class Script(scripts.Script):
    def title(self):
        return "Poor man's outpainting (fixed)"

    def show(self, is_img2img):
        """
        Fix for Bug 4:
        Only show this script in img2img mode where init_images are available.
        """
        return is_img2img

    def ui(self, is_img2img):
        """
        Fix for Bug 4 (continued):
        Guard on is_img2img to ensure UI is only shown when appropriate.
        However, since show() already handles this, we can still create the UI
        but it won't be displayed in txt2img mode.
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

        # Fix for Bug 2:
        # Add type="index" to return integer index instead of string.
        # This matches what p.inpainting_fill expects.
        inpainting_fill = gr.Radio(
            label="Masked content",
            choices=["fill", "original", "latent noise", "latent nothing"],
            value="fill",
            type="index",  # Fixed: return index (0, 1, 2, 3) instead of string
            elem_id=self.elem_id("inpainting_fill"),
        )

        # Fix for Bug 1 + Bug 3:
        # - Remove type="index" so it returns strings like ["left", "right"]
        # - Set default value to at least one direction to prevent empty selection
        direction = gr.CheckboxGroup(
            label="Outpainting direction",
            choices=["left", "right", "up", "down"],
            value=["right"],  # Fixed: default to at least one direction (Bug 3)
            # Fixed: removed type="index" so it returns strings (Bug 1)
            elem_id=self.elem_id("direction"),
        )

        return [pixels, mask_blur, inpainting_fill, direction]

    def run(self, p, pixels, mask_blur, inpainting_fill, direction):
        """
        Fixed run method that handles:
        - Validates init_images exist (Bug 4)
        - Correctly uses inpainting_fill as integer index (Bug 2)
        - Correctly handles direction as list of strings (Bug 1)
        - Validates direction is not empty (Bug 3)
        """

        # Fix for Bug 4:
        # Validate that init_images exists and is not empty before proceeding.
        if not p.init_images or len(p.init_images) == 0:
            raise ValueError(
                "Outpainting requires an initial image. "
                "Please use img2img mode or provide an initial image."
            )

        # Fix for Bug 3:
        # Validate that at least one direction is selected.
        if not direction or len(direction) == 0:
            raise ValueError(
                "At least one outpainting direction must be selected. "
                "Please select 'left', 'right', 'up', or 'down'."
            )

        initial_seed = None
        initial_info = None

        # Fix for Bug 2: inpainting_fill is now an integer index (0, 1, 2, 3)
        # which matches what p.inpainting_fill expects.
        p.mask_blur = mask_blur * 2
        p.inpainting_fill = inpainting_fill  # Now correctly an integer
        p.inpaint_full_res = False

        # Fix for Bug 1:
        # direction is now a list of strings like ["left", "right"],
        # so we can check for strings directly.
        left = pixels if "left" in direction else 0
        right = pixels if "right" in direction else 0
        up = pixels if "up" in direction else 0
        down = pixels if "down" in direction else 0

        # Fix for Bug 4: We've already validated init_images exists above
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
            f"Poor man's outpainting (fixed) will process a total of {len(work)} images "
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

