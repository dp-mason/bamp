import numpy as np
import yaml
import os
import sys
import shutil
import logging

from PIL import Image
from PIL.ImageFile import ImageFile as ImageFile
from typing import List, Tuple

from importlib import resources
from pathlib import Path

from .viscolor import add_pledit_data, add_viscolor_data

from .utils import create_placeholder_image, dilate_box_mask, find_bamp_textures
from .viscolor import extract_viscolor_into_txt, extract_pledit_into_txt

from .pixel_font import write_pixel_comment

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Open and read the YAML file
winamp_spec = resources.open_text("bamp", "winamp_skin_specification.yaml")
WINAMP_SPEC: dict = yaml.safe_load(winamp_spec)
winamp_spec.close()

# TODO: Create "region.txt" file to support transparency


# TODO: Unused. Either call this function or delete it
# takes a list of images and stacks them one on top of the other
# with the first image in the list taking he back and the last being on top
def composite_image_stack(image_filepaths: List[str]):
    img: Image.Image = Image.open(image_filepaths.pop(0))

    for img_fp in image_filepaths:
        img.alpha_composite(Image.open(img_fp))

    return img


def within_bounds(
    im: Image.Image, coord: Tuple[int, int], exit_on_fail: bool = False
) -> bool:
    if not (
        coord[0] >= 0
        and coord[0] <= im.width
        and coord[1] >= 0
        and coord[1] <= im.height
    ):
        logging.warning(
            f"region {coord} is outside image range:\n\twidth: {im.width}\n\t"
            f"height: {im.height}"
        )
        if exit_on_fail:
            raise Exception("fail on out of bounds")
        return False
    return True


# TODO: incomplete sketch
def paste_region_to_file(
    src: Image.Image,
    src_region: tuple[int, int, int, int],
    dest_output_path: str,
    dest_region: tuple[int, int, int, int],
    multiply=None,
):
    # check whether source region is withing bounds of input
    within_bounds(src, src_region[:2])
    within_bounds(src, src_region[2:])

    out_img = Image.open(dest_output_path)

    # check whether dest region is withing bounds of output
    within_bounds(out_img, dest_region[:2])
    within_bounds(out_img, dest_region[2:])

    subsct_img = src.crop(src_region)

    if multiply is not None:
        if multiply < 1:
            divisor = int(1 / multiply)
            subsct_img = subsct_img.resize(
                (int(subsct_img.width / divisor), int(subsct_img.height / divisor))
            )
        else:
            multiply = int(multiply)
            subsct_img = subsct_img.resize(
                (subsct_img.width * multiply, subsct_img.height * multiply),
                resample=Image.Resampling.NEAREST,  # don't smooth the spectrum when enlarging
            )

    out_img.paste(subsct_img, dest_region[0:2])

    out_img.save(dest_output_path, out_img.format)

    return


def bamp_to_winamp(
    winamp_dir,
    bamp_dir,
    save_comps=False,
    delete_existing=False,
    pad_slider_edges=False,
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
            if fn.lower()[-4:] in [".bmp", ".png", ".txt"]:
                os.remove(os.path.join(winamp_dir, fn))
    else:
        sys.exit(f"Non-empty directory exists at path {winamp_dir}")

    # Create empty placeholder winamp files
    for filename, f_md in WINAMP_SPEC["winamp"].items():
        full_output_path: str = os.path.join(winamp_dir, filename)

        if not os.path.exists(full_output_path):
            # get the resolution of this file from the WINAMP_SPEC
            new_map_res = tuple(WINAMP_SPEC["winamp"][filename]["resolution"])
            create_placeholder_image(full_output_path, new_map_res, winamp_file=True)

    im = None

    for bamp_file_name, mappings in WINAMP_SPEC["bamp"].items():
        curr_abs_fp = os.path.join(bamp_dir, bamp_file_name)

        if im is None:
            im = (Image.open(curr_abs_fp)).convert("RGBA")
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
            # check if destination winamp map exists
            winamp_file_name = mapdata["dest"]
            winamp_out_fpath: str = os.path.join(winamp_dir, winamp_file_name)
            input_region = tuple(mapdata["region"])
            output_region = tuple(WINAMP_SPEC["winamp"][winamp_file_name][mapname])
            mult = None  # resize factor

            # allow an unspecified balance/volume handle to be ignored
            if mapdata.get("optional_handle") is not None:
                # open original layer without compositing
                orig_img = Image.open(curr_abs_fp).convert("RGBA")

                # check whether the section for the pan handle is completely transparent
                handle_region = np.array(orig_img.crop(input_region))[:, :, 3]
                if handle_region.all() < 1:
                    logging.info(
                        f"optional handle {mapname} was not designed, cropping {winamp_file_name}"
                    )
                    # no balance/pan handle was specified, crop it from the balance.bmp
                    # image so that no sliding balance/pan handle is used
                    with Image.open(winamp_out_fpath) as winout_img:
                        new_res = WINAMP_SPEC["winamp"][winamp_file_name][
                            "resolution_without_handle"
                        ]
                        box_coords = (0, 0, new_res[0] - 1, new_res[1] - 1)

                        winout_img = winout_img.crop(box_coords)
                        winout_img.save(winamp_out_fpath)
                    continue
                else:
                    logging.info(curr_abs_fp)
                    logging.info(f"{mapname} is present")
                    logging.info(handle_region)
            elif mapname == "eq_viz_spectrum":
                mult = 0.25

            # sometimes the players show part of the winamp image texture they arent
            # supposed to when fractionally scaled, this allows the background composite to be
            # included in the outer perimeter of the element (according to the spec)
            if mapdata.get("allow_bleed") and pad_slider_edges:
                input_region = dilate_box_mask(input_region, mapdata["allow_bleed"])
                output_region = dilate_box_mask(output_region, mapdata["allow_bleed"])

            # try:
            logging.debug(
                f"Remapping {mapname} to {winamp_file_name}:{mapname} using"
                f" target region: {output_region}.\n\n"
            )
            paste_region_to_file(
                im, input_region, winamp_out_fpath, output_region, mult
            )
            # except Exception as e:
            #     logging.error(
            #         f"Error occurred while remapping {mapname} to {winamp_file_name}:{mapname} using"
            #         f" target region: {output_region}.\n\n{e}"
            #     )
            #     sys.exit(1)

        if bamp_file_name == "font_and_palette.png":
            v_lines = extract_viscolor_into_txt(im, WINAMP_SPEC["text_extras"])
            with open(os.path.join(winamp_dir, "viscolor.txt"), "w") as viscolor_f:
                viscolor_f.writelines(v_lines)

            p_lines = extract_pledit_into_txt(im, WINAMP_SPEC["text_extras"])
            with open(os.path.join(winamp_dir, "pledit.txt"), "w") as pledit_f:
                pledit_f.writelines(p_lines)

    # Write the calling card to file
    calling_card_lines = WINAMP_SPEC["CALLING_CARD_TEXT"]
    with open(os.path.join(winamp_dir, "bamp.txt"), "w") as pledit_f:
        pledit_f.writelines(calling_card_lines)


def winamp_to_bamp(winamp_dir, bamp_dir, delete_existing=False):
    if not os.path.exists(bamp_dir):
        os.makedirs(bamp_dir)
    elif (
        delete_existing
        or input(f"Delete Existing Bamp Skin at {bamp_dir}?: ").lower().strip() == "y"
    ):
        # Clear the bamp diectory
        for map_fn in os.listdir(bamp_dir):
            if map_fn.lower()[-4:] in [".png", ".txt"]:
                os.remove(os.path.join(bamp_dir, map_fn))
    else:
        sys.exit(f"Non-empty directory exists at path {bamp_dir}")

    for bamp_fn, mappings in WINAMP_SPEC["bamp"].items():
        # Create placeholder bamp file
        full_bamp_path: str = os.path.join(bamp_dir, bamp_fn)
        create_placeholder_image(
            full_bamp_path,
            tuple(WINAMP_SPEC["BAMP_RESOLUTION"]),
            winamp_file=False,
        )

        for mapname, mapdata in mappings.items():
            logging.debug(f"MAPNAME: {mapname}")
            winamp_file_name = mapdata["dest"]
            full_winamp_path: str = os.path.join(winamp_dir, winamp_file_name)
            input_region = tuple(WINAMP_SPEC["winamp"][winamp_file_name][mapname])

            # allow optional winamp files to be excluded
            if not os.path.exists(full_winamp_path):
                # TODO: this is not the appropriate way to do this
                if (WINAMP_SPEC["winamp"][winamp_file_name]).get("optional"):
                    continue
                else:
                    raise ValueError(
                        f"Expected file {full_winamp_path} does not exist. Optional is set to - {(WINAMP_SPEC['winamp'][winamp_file_name]).get('optional')}"
                    )
            assert os.path.exists(full_winamp_path)
            im = Image.open(full_winamp_path, "r")

            # Try to catch corrupted bmp files
            try:
                im_arr = np.array(im)
                im.close()
            except ValueError as e:
                print(f"BMP decode failed for {full_winamp_path}:\n\t{e}")
                return None

            im = Image.fromarray(im_arr).convert("RGB")

            output_region = tuple(mapdata["region"])
            mult = None

            # check if balance/volume handle has been intentionally cropped from balance bitmap
            if mapdata.get("optional_handle") is not None:
                if (
                    im.height
                    <= WINAMP_SPEC["winamp"][winamp_file_name][
                        "resolution_without_handle"
                    ][1]
                ):
                    logging.info(
                        f"winamp files intentionally ignore {mapname}, skipping"
                    )
                    continue
            elif mapname == "eq_viz_spectrum":
                # multiply size by 4
                mult = 4

            try:
                paste_region_to_file(
                    im, input_region, full_bamp_path, output_region, mult
                )
            except Exception as e:
                sys.exit(
                    f"Error occurred while remapping {full_winamp_path}:{mapname} to {full_bamp_path}:{mapname} using"
                    f"target region: {output_region}.\n\n{e}"
                )

        if bamp_fn == "font_and_palette.png":
            sample_size = WINAMP_SPEC["text_extras"]["COLOR_SAMPLE_SIZE"]
            pledit_start_pos = WINAMP_SPEC["text_extras"]["PLEDIT_START"]
            viscolor_start_pos = WINAMP_SPEC["text_extras"]["VISCOLOR_START"]
            img = Image.open(full_bamp_path)
            try:
                add_pledit_data(
                    os.path.join(winamp_dir, "pledit.txt"),
                    img,
                    pledit_start_pos,
                    sample_size,
                )
            except Exception as e:
                logging.exception(
                    f"Encountered an unknown error while processing pledit text\n\n{e}"
                )

            viscolor_path = os.path.join(winamp_dir, "viscolor.txt")
            if os.path.exists(viscolor_path):
                try:
                    add_viscolor_data(
                        os.path.join(winamp_dir, "viscolor.txt"),
                        img,
                        viscolor_start_pos,
                        WINAMP_SPEC["text_extras"],
                    )
                except Exception as e:
                    logging.exception(
                        f"Encountered an unknown error while processing viscolor text\n\n{e}"
                    )

            eq_comment = write_pixel_comment("EQ Adjust Spectrum", img)

            img.paste(
                eq_comment,
                (
                    mappings["eq_viz_spectrum"]["region"][0] + 6,
                    mappings["eq_viz_spectrum"]["region"][1] + 20,
                ),
            )
            # paste_region_to_file(
            #     eq_comment,
            #     (0, 0, eq_comment.width, eq_comment.height),
            #     curr_abs_fp,
            #     (
            #         mappings["eq_viz_spectrum"]["region"][0] + 6,
            #         mappings["eq_viz_spectrum"]["region"][1] + 20,
            #         mappings["eq_viz_spectrum"]["region"][0] + 6 + eq_comment.width,
            #         mappings["eq_viz_spectrum"]["region"][1] + 20 + eq_comment.height,
            #     ),
            # )
            img.save(full_bamp_path)

    # Clear the to_bamp diectory
    return


def unpack_archive_input(src_path) -> str:
    if src_path.endswith(".wsz"):
        # rename .wsz -> .zip
        src_renamed = f"{src_path[:-4]}.zip"
        os.rename(src_path, src_renamed)
        src_path = src_renamed

    new_dirpath = src_path[0:-4]  # remove .zip
    shutil.unpack_archive(src_path, new_dirpath)

    return new_dirpath


def standardize_file_name(src_path: str, standard_fname: str, alt_fnames: List[str]):
    src_dir_files = os.listdir(src_path)

    for alt_fn in alt_fnames:
        if alt_fn not in src_dir_files:
            continue
        os.rename(
            os.path.join(src_path, alt_fn), os.path.join(src_path, standard_fname)
        )
        return True

    return False


def sanitize_winamp_input(src_path) -> Tuple[str, List[str]]:
    # check if directory is a winamp skin

    # Get the list of all files that make up a winamp skin
    WINAMP_FILES = (WINAMP_SPEC["winamp"]).keys()

    dirfiles = os.listdir(src_path)

    extra_files = []

    if "main.bmp" not in [df.lower() for df in dirfiles]:
        new_src_path = None

        # check if there is a nested dir where the actual winamp skin resides
        for fn in dirfiles:
            curr_fp = os.path.join(src_path, fn)
            if os.path.isdir(curr_fp) and "main.bmp" in [
                df.lower() for df in os.listdir(curr_fp)
            ]:
                # dir with all the winamp files has been found
                new_src_path = os.path.join(src_path, fn)
            else:
                extra_files.append(curr_fp)
        if new_src_path is None:
            sys.exit(
                "Unable to find winamp src dir in first level of directory structure"
            )
        src_path = new_src_path
        dirfiles = os.listdir(src_path)

    for fname in dirfiles:
        fname_lower = fname.lower()
        # TODO: I would like to a better job preserving the old version of pledit and viscolor files
        #   also, I would like to compare against the file names in the specification in this conditional
        if fname_lower.endswith((".bmp", ".cur")) or fname_lower in [
            "pledit.txt",
            "viscolor.txt",
        ]:
            os.rename(
                os.path.join(src_path, fname), os.path.join(src_path, fname_lower)
            )
        else:
            extra_files.append(os.path.join(src_path, fname))

    # Update dirfiles list with lowered filenames
    dirfiles = os.listdir(src_path)

    # Verify that all files needed in the specification are present
    # standardize any alternate names
    # lowercase all filenames for files that are not extraneous
    # add all extraneous files to extra_files
    for filename in WINAMP_FILES:
        if filename in dirfiles:
            continue
        else:
            FILE_SPEC_INFO = WINAMP_SPEC["winamp"][filename]
            if FILE_SPEC_INFO.get("optional"):
                logging.warning(
                    f"Optional file {filename} is missing from the input winamp skin"
                )
                continue
            elif "alt_names" in FILE_SPEC_INFO:
                if not standardize_file_name(
                    src_path, filename, FILE_SPEC_INFO["alt_names"]
                ):
                    sys.exit(
                        f"Alt names specified for "
                        f"{filename}, but none were identified in winamp files:\n\t{dirfiles}"
                    )
            else:
                sys.exit(
                    f"Winamp/Bamp skin is missing expected file or alternate name not specified: "
                    f"{filename}\n\n{src_path}\n{dirfiles}",
                )

    # resize nums_ex.bmp to the standard size
    with Image.open(os.path.join(src_path, "nums_ex.bmp")) as nums_ex_img:
        standard_res = WINAMP_SPEC["winamp"]["nums_ex.bmp"]["resolution"]
        if nums_ex_img.width != standard_res[0]:
            logging.info(
                f"resizing nums_ex.bmp from {nums_ex_img.width} to {standard_res[0]}"
            )
            extended = Image.new(
                nums_ex_img.mode,
                (standard_res[0], standard_res[1]),
                color=(255, 0, 0),  # TODO: background color
            )

            # Paste the original image at the top-left corner
            extended.paste(nums_ex_img, (0, 0))

            extended.save(os.path.join(src_path, "nums_ex.bmp"))

    return src_path, extra_files


def convert(
    to_winamp,
    winamp_dir,
    bamp_dir,
    save_comps,
    delete_existing,
    pad_slider_edges=False,
):
    src_path: str = bamp_dir if to_winamp else winamp_dir
    dest_path: str = winamp_dir if to_winamp else bamp_dir

    if dest_path.endswith(".zip"):
        zip_output = True
        dest_path = dest_path[0:-4]
    else:
        zip_output = False

    # Open a zip archive if it has been passed as the source
    # No zip bomb checks are made at this stage, handle before calling this function
    if src_path[-4:] in [".zip", ".wsz"]:
        src_path = unpack_archive_input(src_path)

    extra_files = []

    if to_winamp:
        # process bamp input if converting to winamp
        # TODO: capture extra files
        src_path = find_bamp_textures(src_path)
        bamp_to_winamp(
            dest_path, src_path, save_comps, delete_existing, pad_slider_edges
        )
    else:
        # process winamp input if converting to bamp
        src_path, extra_files = sanitize_winamp_input(src_path)
        winamp_to_bamp(src_path, dest_path, delete_existing)

    # move extraneous files to the destination directory under reserved subdir
    if len(extra_files) > 0:
        dest_extra = os.path.join(dest_path, "extra")
        # allow extraneous files to accumulate in "extra"
        os.makedirs(dest_extra, exist_ok=True)
        for curr_path in extra_files:
            curr_dest = os.path.join(dest_extra, os.path.basename(curr_path))
            if os.path.isdir(curr_path):
                shutil.copytree(curr_path, curr_dest, dirs_exist_ok=True)
            else:
                shutil.copyfile(curr_path, curr_dest)

    if zip_output:
        base_name = os.path.basename(dest_path)
        abs_dest_path = os.path.abspath(dest_path)
        shutil.make_archive(base_name, "zip", abs_dest_path)
        if Path(abs_dest_path).parent != Path(os.path.abspath(os.curdir)):
            logging.info(f"{abs_dest_path} is not same as {os.path.abspath(os.curdir)}")
            shutil.move(f"{base_name}.zip", Path(abs_dest_path).parent)

    return
