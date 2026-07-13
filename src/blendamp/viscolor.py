from PIL import Image
from typing import Tuple
import numpy as np
import sys
from typing import List


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
        rgb = [int(strval.strip()) for strval in visline.split(",")[0:3]]

        color_image = Image.fromarray(
            np.full((sample_size, sample_size, 3), rgb[:3], dtype=np.uint8)
        )

        im.paste(color_image, (start_pos[0], start_pos[1] + row * sample_size))

        row += 1


def extract_viscolor_into_txt(im: Image.Image, WINAMP_TEXT_EXTRAS: dict) -> List[str]:
    total = WINAMP_TEXT_EXTRAS["VISCOLOR_TOTAL"]
    sample_size = WINAMP_TEXT_EXTRAS["COLOR_SAMPLE_SIZE"]
    viscolor_comments = WINAMP_TEXT_EXTRAS["VISCOLOR_COMMENTS"]

    # top left corner
    start = WINAMP_TEXT_EXTRAS["VISCOLOR_START"]
    # bottom right corner
    end = [start[0] + sample_size, start[1] + (total * sample_size)]

    # crop for simplicity
    viscolor_img: Image.Image = im.crop(start + end)

    lines = []
    for index in range(0, total):
        # sample the innermost pixel and save it as a text line

        y_coord = (sample_size / 2) + (sample_size * index)
        pixel = viscolor_img.getpixel((sample_size / 2, y_coord))

        if type(pixel) is not tuple:
            sys.exit(
                f'pixel retrieval returned {type(pixel)} instead of expected "tuple"'
            )

        # write the pixel to viscolor txt line
        currline = str(pixel[0]) + ", " + str(pixel[1]) + ", " + str(pixel[2])
        # align comments vertically
        num_spaces = 15 - len(currline)
        currline = currline + (" " * num_spaces) + viscolor_comments[index] + "\n"
        lines.append(currline)

    return lines


def extract_pledit_into_txt(im: Image.Image, WINAMP_TEXT_EXTRAS: dict) -> List[str]:
    keys = WINAMP_TEXT_EXTRAS["PLEDIT_FIELDS"]
    sample_size = WINAMP_TEXT_EXTRAS["COLOR_SAMPLE_SIZE"]

    # top left corner
    start = WINAMP_TEXT_EXTRAS["PLEDIT_START"]
    # bottom right corner (font is not )
    end = [start[0] + sample_size, start[1] + ((len(keys) - 1) * sample_size)]

    # crop for simplicity
    viscolor_img: Image.Image = im.crop(start + end)

    lines = []
    lines.append("[Text]\n")
    for index in range(0, len(keys)):
        # sample the innermost pixel and save it as a text line

        value = None
        if keys[index] == "Font":
            value = WINAMP_TEXT_EXTRAS["PLEDIT_FONT"]
        else:
            y_coord = (sample_size / 2) + (sample_size * index)
            pixel = viscolor_img.getpixel((sample_size / 2, y_coord))

            if type(pixel) is not tuple:
                sys.exit(
                    f'pixel retrieval returned {type(pixel)} instead of expected "tuple"'
                )

            value = ("#%02x%02x%02x" % (pixel[0], pixel[1], pixel[2])).upper()

        # write the pixel to viscolor txt line
        currline = keys[index] + "=" + value + "\n"
        lines.append(currline)

    return lines
