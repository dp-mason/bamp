import os
from PIL import Image
import click
from typing import Tuple
import numpy as np

from .utils import create_placeholder_image


def add_pledit_data(
    pledit_path: str, im: Image.Image, start_pos: Tuple[int, int], sample_size: int
):
    pledit_lines = None
    with open(pledit_path, "r") as pledit_f:
        pledit_lines = pledit_f.readlines()

    text_sect = False
    pledit_colors = {}
    # build dictionary from the "[text]" section of pledit file
    for pledit_ln in pledit_lines:
        pledit_ln = pledit_ln.strip()

        if pledit_ln.lower() == "[text]":
            # indicate that the text section has been found then proceed to next line
            text_sect = True
            continue
        elif not text_sect:
            continue

        if "=" in pledit_ln:
            # build dictionary entry for this color
            keyval = [s.strip() for s in pledit_ln.split("=")[:2]]

            if keyval[0].lower() == "font":
                continue

            hexc = (keyval[1]).lstrip("#")

            # convert hex pairs to rgb values
            rgb_color = tuple(int(hexc[i : i + 2], 16) for i in (0, 2, 4))

            pledit_colors[keyval[0]] = rgb_color
        else:
            if text_sect and "[" in pledit_ln:
                # text section is over, break
                break
            else:
                # skip empty and irrelevant lines
                continue

    # paste to output file according to key order
    row = 0
    for _, color in pledit_colors.items():
        color_image = Image.fromarray(
            np.full((sample_size, sample_size, 3), color, dtype=np.uint8)
        )
        sample_start = (
            start_pos[0],
            start_pos[1] + sample_size * row,
        )
        im.paste(color_image, sample_start)

        row += 1


def add_viscolor_data(
    viscolor_path: str, im: Image.Image, start_pos: Tuple[int, int], sample_size: int
):
    viscolor_lines = None
    with open(viscolor_path, "r") as viscolor_f:
        viscolor_lines = viscolor_f.readlines()

    row = 0
    for visline in viscolor_lines:
        # strip comment
        comment_ind = visline.rfind("//")
        if comment_ind > -1:
            visline = visline[: visline.rfind("//")]
        visline = visline.strip()
        rgb = [int(strval.strip()) for strval in visline.split(",")]

        color_image = Image.fromarray(np.full((8, 8, 3), rgb[:3], dtype=np.uint8))

        im.paste(color_image, (start_pos[0], start_pos[1] + row * sample_size))

        row += 1
