from PIL import Image
from PIL.ImageFile import ImageFile as ImageFile
from typing import List

import numpy as np
import yaml
import os
import sys
import shutil

import click
from zipfile import is_zipfile

# TODO: Create "region.txt" file to support transparency


# TODO: Unused. Either call this function or delete it
# takes a list of images and stacks them one on top of the other
# with the first image in the list taking he back and the last being on top
def composite_image_stack(image_filepaths: List[str]):
    img: Image.Image = Image.open(image_filepaths.pop(0))

    for img_fp in image_filepaths:
        img.alpha_composite(Image.open(img_fp))

    return img


# TODO: incomplete sketch
def paste_region_to_file(
    src: Image.Image,
    src_region: tuple[float, float, float, float],
    dest_output_path: str,
    dest_region: tuple[int, int, int, int],
):
    out_img = Image.open(dest_output_path)
    subsct_img = src.crop(src_region)

    out_img.paste(subsct_img, dest_region[0:2])

    out_img.save(dest_output_path, out_img.format)
    return


def create_placeholder_image(img_path: str, res: tuple[int, int], mode: str = "RGBA"):
    # create an new image and fill with magenta, which is the transparent color
    match mode:
        case "RGBA":
            winamp_img = Image.new("RGBA", res, (0, 0, 0, 0))
        case "RGB":
            winamp_img = Image.new("RGB", res, (255, 0, 255))
        case _:
            sys.exit('Please supply "RGB" or "RGBA" as the mode')

    winamp_img.save(img_path)


def blendamp_to_winamp(
    winamp_dir, blendamp_dir, save_comps=False, delete_existing=False
):

    # clear winamp_dir
    # TODO: ask whether to delete, and add flag that overrides question
    if not os.path.exists(winamp_dir):
        os.makedirs(winamp_dir)
    elif (
        delete_existing
        or input(f"Delete Existing Winamp Skin at {winamp_dir}?: ").lower().strip()
        == "y"
    ):
        for fn in os.listdir(winamp_dir):
            if fn.endswith(".bmp") or fn.endswith(".png"):
                os.remove(os.path.join(winamp_dir, fn))
    else:
        sys.exit(f"Non-empty directory exists at path {winamp_dir}")

    # Open and read the YAML file
    with open("winamp_skin_specification.yaml", "r") as file:
        CONFIG: dict = yaml.safe_load(file)

    # Create empty placeholder winamp files
    for filename, f_md in CONFIG["winamp"].items():
        full_output_path: str = os.path.join(winamp_dir, filename)

        if not os.path.exists(full_output_path):
            # get the resolution of this file from the CONFIG
            new_map_res = tuple(CONFIG["winamp"][filename]["resolution"])
            create_placeholder_image(full_output_path, new_map_res, "RGB")

    im = None

    for bamp_file_name, mappings in CONFIG["blendamp"].items():
        curr_abs_fp = os.path.join(blendamp_dir, bamp_file_name)

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

            if save_comps:
                im.save(os.path.join(winamp_dir, "COMPOSITED_" + bamp_file_name))

        for mapname, mapdata in mappings.items():
            # TODO: turn this loop body into a function that takes a source and dest image file paths and regions
            # capture the subsection of the image that represents a specific element

            # check if destination winamp map exists
            winamp_file_name = mapdata["dest"]
            full_output_path: str = os.path.join(winamp_dir, winamp_file_name)
            input_region = tuple(mapdata["region"])
            output_region = tuple(CONFIG["winamp"][winamp_file_name][mapname][0:2])

            try:
                paste_region_to_file(im, input_region, full_output_path, output_region)
            except Exception as e:
                sys.exit(
                    f"Error occurred while remapping {mapname} to {winamp_file_name}:{mapname} using"
                    f"target region: {output_region}.\n\n{e}"
                )


def winamp_to_blendamp(winamp_dir, blendamp_dir, delete_existing=False):
    if not os.path.exists(blendamp_dir):
        os.makedirs(blendamp_dir)
    elif (
        delete_existing
        or input(f"Delete Existing Blendamp Skin at {blendamp_dir}?: ").lower().strip()
        == "y"
    ):
        # Clear the blendamp diectory
        for map_fn in os.listdir(blendamp_dir):
            if map_fn.endswith(".png"):
                os.remove(os.path.join(blendamp_dir, map_fn))
    else:
        sys.exit(f"Non-empty directory exists at path {blendamp_dir}")

    # Open and read the YAML file
    with open("winamp_skin_specification.yaml", "r") as file:
        CONFIG: dict = yaml.safe_load(file)

    for bamp_fn, mappings in CONFIG["blendamp"].items():
        # Create placeholder blendamp file
        full_blendamp_path: str = os.path.join(blendamp_dir, bamp_fn)
        create_placeholder_image(
            full_blendamp_path, tuple(CONFIG["BLENDAMP_RESOLUTION"]), "RGBA"
        )

        for mapname, mapdata in mappings.items():
            winamp_file_name = mapdata["dest"]
            full_winamp_path: str = os.path.join(winamp_dir, winamp_file_name)
            input_region = tuple(CONFIG["winamp"][winamp_file_name][mapname])

            im = Image.open(full_winamp_path)
            im_arr = np.array(im)
            im.close()
            im = Image.fromarray(im_arr).convert("RGB")

            output_region = tuple(mapdata["region"])

            try:
                paste_region_to_file(
                    im, input_region, full_blendamp_path, output_region
                )
            except Exception as e:
                sys.exit(
                    f"Error occurred while remapping {full_winamp_path}:{mapname} to {full_blendamp_path}:{mapname} using"
                    f"target region: {output_region}.\n\n{e}"
                )

    # Clear the to_blendamp diectory
    return


def convert(to_winamp, winamp_dir, blendamp_dir, save_comps, delete_existing):

    src_path: str = blendamp_dir if to_winamp else winamp_dir
    dest_path: str = winamp_dir if to_winamp else blendamp_dir

    if dest_path.endswith(".zip"):
        zip_output = True
        dest_path = dest_path[0:-4]
    else:
        zip_output = False

    # Open a zip archive if it has been passed as the source
    # No zip bomb checks are made at this stage, sanitize before calling this function
    if src_path.endswith(".zip"):
        # if not is_zipfile(src_path):
        #     sys.exit(f"Bad zip file: {src_path}")
        shutil.unpack_archive(src_path, src_path[0:-4])
        # Remove .zip extension
        src_path = src_path[0:-4]

    if to_winamp:
        blendamp_to_winamp(dest_path, src_path, save_comps, delete_existing)
    else:
        winamp_to_blendamp(src_path, dest_path, delete_existing)

    if zip_output:
        shutil.make_archive(
            os.path.basename(dest_path), "zip", os.path.abspath(dest_path)
        )

    return


@click.command()
@click.option("--to-winamp/--to-blendamp", default=True)
@click.option("--winamp-dir", default="winamp_skin")
@click.option("--blendamp-dir", default="blendamp")
@click.option("--save-comps", is_flag=True, default=False)
@click.option("--delete-existing", is_flag=True, default=False)
def cli_convert(to_winamp, winamp_dir, blendamp_dir, save_comps, delete_existing):
    convert(to_winamp, winamp_dir, blendamp_dir, save_comps, delete_existing)
    return


if __name__ == "__main__":
    cli_convert()
