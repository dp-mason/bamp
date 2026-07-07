import os
from PIL import Image
import click
import blendamp


def convert_pledit(pledit_path: str):
    viscolor_lines = None
    with open(pledit_path, "r") as pledit_f:
        pledit_lines = pledit_f.readlines()

    impath = os.path.join(os.curdir, "test_viscolor.png")

    im = blendamp.Image.open(impath, "r")

    text_sect = False
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
        else:
            if text_sect and "[" in pledit_ln:
                # text section is over, break
                break
            else:
                # skip empty and irrelevant lines
                continue
            


@click.command()
@click.option("--viscolor-path", default="None")
@click.option("--pledit-path", default="None")
def viscolor_convert(winamp_path: str = "None"):
    viscolor_lines = None
    with open(winamp_path, "r") as viscolor_f:
        viscolor_lines = viscolor_f.readlines()

    impath = os.path.join(os.curdir, "test_viscolor.png")

    blendamp.create_placeholder_image(impath, (275, 348), False)
    im = blendamp.Image.open(impath, "r")

    row = 0
    for visline in viscolor_lines:
        # strip comment
        comment_ind = visline.rfind("//")
        if comment_ind > -1:
            visline = visline[: visline.rfind("//")]
        visline = visline.strip()
        rgb = [int(strval.strip()) for strval in visline.split(",")]

        color_image = Image.fromarray(
            blendamp.np.full((8, 8, 3), rgb[:3], dtype=blendamp.np.uint8)
        )

        im.paste(color_image, (0, 8 * row, 8, 8 * row + 8))
        im.save(impath)

        row += 1

    return


if __name__ == "__main__":
    viscolor_convert()
