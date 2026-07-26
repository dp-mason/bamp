from typing import Tuple
from PIL import Image


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
