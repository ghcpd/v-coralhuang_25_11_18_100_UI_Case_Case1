import math

import modules.scripts as scripts
import gradio as gr
from PIL import Image, ImageDraw

from modules import images, devices
from modules.processing import Processed, process_images
from modules.shared import opts, state


class Script(scripts.Script):
    def title(self):
        return "Poor man's outpainting (fixed version)"

    def show(self, is_img2img):
        """
        FIX for Bug 4:
        Only show this script in img2img mode where init_images are available.
        Return True only when is_img2img is True.
        """
        return is_img2img

    def ui(self, is_img2img):
        """
        FIX for Bug 4 (continued):
        UI only shown in img2img mode now, so we always have init images.
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

        # FIX for Bug 2:
        # Add type="index" so Radio returns integer index (0, 1, 2, 3)
        # instead of string values ("fill", "original", etc.)
        inpainting_fill = gr.Radio(
            label="Masked content",
            choices=["fill", "original", "latent noise", "latent nothing"],
            value="fill",
            type="index",  # FIXED: return index instead of string
            elem_id=self.elem_id("inpainting_fill"),
        )

        # FIX for Bug 1 + Bug 3:
        # - Remove type="index" so CheckboxGroup returns strings ["left", "right", ...]
        #   which matches the string checks in run() method
        # - Set value=["left", "right", "up", "down"] as default to ensure
        #   at least one direction is selected (prevents silent no-op)
        direction = gr.CheckboxGroup(
            label="Outpainting direction",
            choices=["left", "right", "up", "down"],
            value=["left", "right", "up", "down"],  # FIXED: default to all directions
            # type="index" removed - returns strings instead of indices
            elem_id=self.elem_id("direction"),
        )

        return [pixels, mask_blur, inpainting_fill, direction]

    def run(self, p, pixels, mask_blur, inpainting_fill, direction):
        """
        Fixed version with proper type handling:

        - Only runs in img2img mode (Bug 4 fixed via show() method)
        - inpainting_fill is now an integer index (Bug 2 fixed)
        - direction is a list of strings that match our checks (Bug 1 fixed)
        - direction defaults to all directions, preventing silent no-op (Bug 3 fixed)
        - Added validation to ensure at least one direction is selected
        """

        # Validation: ensure at least one direction is selected
        if not direction or len(direction) == 0:
            raise ValueError(
                "At least one outpainting direction must be selected. "
                "Please check at least one of: left, right, up, down."
            )

        # Validation: ensure init_images exists (defensive check)
        if not p.init_images or len(p.init_images) == 0:
            raise ValueError(
                "No initial image provided. This script requires an input image "
                "(img2img mode only)."
            )

        initial_seed = None
        initial_info = None

        # FIX for Bug 2: inpainting_fill is now an integer index,
        # can be assigned directly to p.inpainting_fill
        p.mask_blur = mask_blur * 2
        p.inpainting_fill = inpainting_fill
        p.inpaint_full_res = False

        # FIX for Bug 1 + 3:
        # direction is now a list of strings (e.g. ["left", "right"])
        # and we're guaranteed to have at least one direction
        left = pixels if "left" in direction else 0
        right = pixels if "right" in direction else 0
        up = pixels if "up" in direction else 0
        down = pixels if "down" in direction else 0

        # FIX for Bug 4:
        # show() method ensures we only run in img2img mode,
        # but we still validate defensively above
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
        # Calculate rectangle coordinates with bounds checking
        mask_x0 = left + (mask_blur * 2 if left > 0 else 0)
        mask_y0 = up + (mask_blur * 2 if up > 0 else 0)
        mask_x1 = mask.width - right - (mask_blur * 2 if right > 0 else 0)
        mask_y1 = mask.height - down - (mask_blur * 2 if down > 0 else 0)
        # Ensure valid rectangle (x1 >= x0, y1 >= y0)
        if mask_x1 > mask_x0 and mask_y1 > mask_y0:
            draw.rectangle((mask_x0, mask_y0, mask_x1, mask_y1), fill="black")

        latent_mask = Image.new("L", (img.width, img.height), "white")
        latent_draw = ImageDraw.Draw(latent_mask)
        # Calculate latent mask rectangle coordinates with bounds checking
        latent_x0 = left + (mask_blur // 2 if left > 0 else 0)
        latent_y0 = up + (mask_blur // 2 if up > 0 else 0)
        latent_x1 = mask.width - right - (mask_blur // 2 if right > 0 else 0)
        latent_y1 = mask.height - down - (mask_blur // 2 if down > 0 else 0)
        # Ensure valid rectangle (x1 >= x0, y1 >= y0)
        if latent_x1 > latent_x0 and latent_y1 > latent_y0:
            latent_draw.rectangle((latent_x0, latent_y0, latent_x1, latent_y1), fill="black")

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
