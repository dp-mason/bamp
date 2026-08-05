from typing import Tuple
from PIL import Image
import os
import logging


def create_placeholder_image(img_path: str, res: tuple[int, int], winamp_file: bool):
    if winamp_file:
        # create an new image and fill with magenta
        winamp_img = Image.new("RGB", res, (255, 0, 255))
        winamp_img.save(img_path, "bmp")
    else:
        bamp_img = Image.new("RGBA", res, (0, 0, 0, 0))
        bamp_img.save(img_path, "png")


def dilate_box_mask(
    box: tuple[int, int, int, int], amount: int
) -> Tuple[int, int, int, int]:
    return (box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1)


# TODO: this might delete files that have been improperly included in directories other than the bamp texture dir
def find_bamp_textures(dirpath: str, level: int = 0):
    if "00.png" in os.listdir(dirpath):
        # presumably found bamp textures
        logging.info("found path containing bamp textures")
        return dirpath
    elif level < 3:
        for subpath in os.listdir(dirpath):
            full_subpath = os.path.join(dirpath, subpath)

            if not os.path.isdir(full_subpath):
                continue

            # recurse down each subdirectory
            if find_bamp_textures(full_subpath, level=level + 1) is not None:
                return full_subpath
            logging.info(f"bamp textures not found in {full_subpath}")

    return None
