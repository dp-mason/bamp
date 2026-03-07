from PIL import Image
from PIL.ImageFile import ImageFile as ImageFile
from typing import List

import numpy as np
import yaml
import os


# takes a list of images and stacks them one on top of the other
# with the first image in the list taking he back and the last being on top
def composite_image_stack(images: List[Image.Image], region: tuple):
    return images[0].crop(region)


BLENDAMP_DIR = os.path.abspath("blendamp")
WINAMP_DIR = os.path.abspath("./winamp_skin")

# clear WINAMP_DIR
if os.path.exists(WINAMP_DIR):
    for fn in os.listdir(WINAMP_DIR):
        if fn.endswith(".bmp"):
            os.remove(os.path.join(WINAMP_DIR, fn))
else:
    os.makedirs(WINAMP_DIR)

# Open and read the YAML file
with open("winamp_skin_specification.yaml", "r") as file:
    CONFIG: dict = yaml.safe_load(file)


# Create empty placeholder winamp files
for filename, f_md in CONFIG["winamp"].items():
    full_output_path: str = os.path.join(WINAMP_DIR, filename)

    if not os.path.exists(full_output_path):
        # get the resolution of this file from the CONFIG
        new_map_res = tuple(CONFIG["winamp"][filename]["resolution"])
        # create an new image and fill with magenta, which is the transparent color
        winamp_img = Image.new("RGB", new_map_res, (255, 0, 255))
        winamp_img.save(full_output_path)

# TODO: Create "region.txt" file to support transparency

image_stack = []

for file_name, mappings in CONFIG["blendamp"].items():
    im: ImageFile = Image.open(os.path.join(BLENDAMP_DIR, file_name))
    im_arr = np.array(im)

    # set all partial transparency to maximum opacity
    im_arr[im_arr[:, :, 3] > 0, 3] = 255
    # set all transparent pixels to magenta for winamp
    im_arr[im_arr[:, :, 3] == 0] = np.array([255, 0, 255, 255])

    res_img = Image.fromarray(im_arr).convert("RGB")

    im.close()

    for mapname, mapdata in mappings.items():
        # capture the subsection of the image that represents a specific element
        subsct_img = res_img.crop(tuple(mapdata["region"]))

        # check if destination winamp map exists
        file_name = mapdata["dest"]
        full_output_path: str = os.path.join(WINAMP_DIR, file_name)

        winamp_img = None

        winamp_img = Image.open(full_output_path)

        target_region = tuple(CONFIG["winamp"][file_name][mapname][0:2])
        try:
            winamp_img.paste(subsct_img, target_region)
        except Exception as e:
            os.error(
                f"Error occurred while remapping {mapname} to {file_name}:{mapname} using"
                f"target region: {target_region}.\n\n{e}"
            )

        with open(full_output_path, "wb") as f:
            winamp_img.save(f, "bmp")
