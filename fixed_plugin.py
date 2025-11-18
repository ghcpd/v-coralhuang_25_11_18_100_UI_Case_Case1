import math
from typing import Sequence, Tuple, Union

import gradio as gr
from PIL import Image, ImageDraw

import modules.scripts as scripts
from modules import devices, images
from modules.processing import Processed, process_images
from modules.shared import opts, state

DIRECTION_CHOICES = ("left", "right", "up", "down")
FILL_CHOICES = ("fill", "original", "latent noise", "latent nothing")
FILL_MAP = {name: idx for idx, name in enumerate(FILL_CHOICES)}


def normalize_direction_input(direction: Union[None, str, int, Sequence[Union[str, int]]]) -> Tuple[str, ...]:
    if direction is None:
        return tuple()

    if isinstance(direction, (str, int)):
        direction = (direction,)

    normalized = []
    for value in direction:
        if isinstance(value, int):
            if 0 <= value < len(DIRECTION_CHOICES):
                normalized.append(DIRECTION_CHOICES[value])
            else:
                raise ValueError(f"Direction index {value} is out of range.")
        elif isinstance(value, str):
            candidate = value.strip().lower()
            if candidate not in DIRECTION_CHOICES:
                raise ValueError(f"Unknown direction '{value}'.")
            normalized.append(candidate)
        else:
            raise ValueError("Direction entries must be strings or integers.")

    # preserve order while removing duplicates
    ordered_unique = []
    for entry in normalized:
        if entry not in ordered_unique:
            ordered_unique.append(entry)
    return tuple(ordered_unique)


def compute_direction_offsets(direction: Sequence[str], pixels: int) -> Tuple[int, int, int, int]:
    if not direction:
        raise ValueError("Select at least one outpainting direction.")

    direction_set = set(direction)
    left = pixels if "left" in direction_set else 0
    right = pixels if "right" in direction_set else 0
    up = pixels if "up" in direction_set else 0
    down = pixels if "down" in direction_set else 0

    return left, right, up, down


def ensure_fill_index(fill_index: Union[str, int]) -> int:
    if isinstance(fill_index, int):
        if 0 <= fill_index < len(FILL_CHOICES):
            return fill_index
        raise ValueError("Inpainting fill index out of range.")

    candidate = fill_index.strip().lower()
    if candidate in FILL_MAP:
        return FILL_MAP[candidate]

    raise ValueError(f"Unknown inpainting fill choice '{fill_index}'.")


class Script(scripts.Script):
    def title(self):
        return "Poor man's outpainting (fixed)"

    def show(self, is_img2img):
        return bool(is_img2img)

    def ui(self, is_img2img):
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

        inpainting_fill = gr.Radio(
            label="Masked content",
            choices=list(FILL_CHOICES),
            value="fill",
            type="index",
            elem_id=self.elem_id("inpainting_fill"),
        )

        direction = gr.CheckboxGroup(
            label="Outpainting direction",
            choices=list(DIRECTION_CHOICES),
            value=["left"],
            elem_id=self.elem_id("direction"),
        )

        return [pixels, mask_blur, inpainting_fill, direction]

    def run(self, p, pixels, mask_blur, inpainting_fill, direction):
        init_images = getattr(p, "init_images", None)
        if not init_images:
            raise ValueError("Outpainting requires an init image from img2img mode.")

        init_img = init_images[0]
        direction_values = normalize_direction_input(direction)
        left, right, up, down = compute_direction_offsets(direction_values, pixels)

        p.mask_blur = mask_blur * 2
        p.inpainting_fill = ensure_fill_index(inpainting_fill)
        p.inpaint_full_res = False

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
        grid_latent_mask = images.split_grid(
            latent_mask, tile_w=p.width, tile_h=p.height, overlap=pixels
        )

        p.n_iter = 1
        p.batch_size = 1
        p.do_not_save_grid = True
        p.do_not_save_samples = True

        work = []
        work_mask = []
        work_latent_mask = []
        work_results = []
        initial_seed = None
        initial_info = None

        for (y, h, row), (_, _, row_mask), (_, _, row_latent_mask) in zip(
            grid.tiles, grid_mask.tiles, grid_latent_mask.tiles
        ):
            for tiledata, tiledata_mask, tiledata_latent_mask in zip(
                row, row_mask, row_latent_mask
            ):
                x, w = tiledata[0:2]

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
        state.job_count = batch_count

        for i in range(batch_count):
            p.init_images = [work[i]]
            p.image_mask = work_mask[i]
            p.latent_mask = work_latent_mask[i]

            state.job = f"Batch {i + 1} out of {batch_count}"
            processed = process_images(p)

            if getattr(p, "seed", None) is None:
                p.seed = processed.seed

            if i == 0:
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

        processed_output = Processed(p, [combined_image], initial_seed, initial_info)
        return processed_output
