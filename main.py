from PIL import Image
from PIL.ImageFile import ImageFile as ImageFile
from typing import List

import numpy as np
import yaml
import os

import click

# TODO: Create "region.txt" file to support transparency


# takes a list of images and stacks them one on top of the other
# with the first image in the list taking he back and the last being on top
def composite_image_stack(image_filepaths: List[str]):
    img: Image.Image = Image.open(image_filepaths.pop(0))

    for img_fp in image_filepaths:
        img.alpha_composite(Image.open(img_fp))

    return img


def blendamp_to_winamp():
    BLENDAMP_DIR = os.path.abspath("blendamp")
    WINAMP_DIR = os.path.abspath("./winamp_skin")

    # clear WINAMP_DIR
    if os.path.exists(WINAMP_DIR):
        for fn in os.listdir(WINAMP_DIR):
            if fn.endswith(".bmp") or fn.endswith(".png"):
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

    im = None

    for bamp_file_name, mappings in CONFIG["blendamp"].items():
        curr_abs_fp = os.path.join(BLENDAMP_DIR, bamp_file_name)

        if im is None:
            im = Image.open(curr_abs_fp)
            im_arr = np.array(im)

            # set all partial transparency to maximum opacity
            im_arr[im_arr[:, :, 3] > 0, 3] = 255
            # set all fully transparent pixels to magenta
            im_arr[im_arr[:, :, 3] == 0] = np.array([255, 0, 255, 255])

            im.close()

            im = Image.fromarray(im_arr).convert("RGBA")
        else:
            # add the current layer to the top of the stack
            # this effectively allows artists to default to the layer below if they
            # havent designed every single element
            im.alpha_composite(Image.open(curr_abs_fp))

            im.save(os.path.join(WINAMP_DIR, bamp_file_name))

        for mapname, mapdata in mappings.items():
            # capture the subsection of the image that represents a specific element
            subsct_img = im.crop(tuple(mapdata["region"]))

            # check if destination winamp map exists
            winamp_file_name = mapdata["dest"]
            full_output_path: str = os.path.join(WINAMP_DIR, winamp_file_name)

            winamp_img = None

            winamp_img = Image.open(full_output_path)

            target_region = tuple(CONFIG["winamp"][winamp_file_name][mapname][0:2])
            try:
                winamp_img.paste(subsct_img, target_region)
            except Exception as e:
                os.error(
                    f"Error occurred while remapping {mapname} to {winamp_file_name}:{mapname} using"
                    f"target region: {target_region}.\n\n{e}"
                )

            winamp_img.save(full_output_path, "bmp")


def winamp_to_blendamp():
    print("winamp_to_blendamp is ACTIVE")
    # Reverse the flow of the pairing dictionary

    # Open and read the YAML file
    with open("winamp_skin_specification.yaml", "r") as file:
        CONFIG: dict = yaml.safe_load(file)

    for bamp_fn, mappings in CONFIG["blendamp"].items():
        for mapname, mapdata in mappings.items():
            winamp_file_name = mapdata["dest"]
            tmp_region = CONFIG["winamp"][winamp_file_name][mapname]
            CONFIG["winamp"][winamp_file_name][mapname] = {}
            tmp_region = CONFIG["winamp"][winamp_file_name][mapname]["region"] = (
                tmp_region
            )
            tmp_region = CONFIG["winamp"][winamp_file_name][mapname]["bamp_file"] = (
                bamp_fn
            )

            print(f"{mapname}\n\t", CONFIG["winamp"][winamp_file_name][mapname])

    # Clear the to_blendamp diectory
    return


@click.command()
@click.option("--to-winamp/--to-blendamp", default=True)
def main(to_winamp):
    print("Main")
    if to_winamp:
        blendamp_to_winamp()
    else:
        winamp_to_blendamp()


if __name__ == "__main__":
    main()
