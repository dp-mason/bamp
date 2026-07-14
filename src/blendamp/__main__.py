from PIL import Image
import click
from . import blendamp
from . import viscolor
from . import pixel_font
from .utils import create_placeholder_image
import logging
import os

bamp_cli_log = logging.Logger("bamp_cli_log", level=logging.DEBUG)


def cli_textcolor_convert(
    viscolor_path: str | None = None, pledit_path: str | None = None
):

    impath = os.path.join(os.curdir, "test_viscolor.png")

    create_placeholder_image(impath, (275, 348), False)
    im = blendamp.Image.open(impath, "r")

    sample_size = blendamp.WINAMP_SPEC["text_extras"]["COLOR_SAMPLE_SIZE"]
    pledit_start_pos = blendamp.WINAMP_SPEC["text_extras"]["PLEDIT_START"]
    viscolor_start_pos = blendamp.WINAMP_SPEC["text_extras"]["VISCOLOR_START"]

    if viscolor_path is not None:
        viscolor.add_viscolor_data(viscolor_path, im, viscolor_start_pos, sample_size)
    if pledit_path is not None:
        viscolor.add_pledit_data(pledit_path, im, pledit_start_pos, sample_size)

    im.save(impath)

    return


#
#
# if __name__ == "__main__":
#     viscolor_convert()


@click.command()
@click.option("--to-winamp/--to-blendamp", default=True)
@click.option("--winamp-dir", default="winamp_skin")
@click.option("--blendamp-dir", default="blendamp")
@click.option("--save-comps", is_flag=True, default=False)
@click.option("--delete-existing", is_flag=True, default=False)
@click.option("--viscolor-path", default=None)
@click.option("--pledit-path", default=None)
@click.option("--text-comment", default=None)
@click.option("--pixel-font-path", default=None)
def cli_convert(
    to_winamp,
    winamp_dir,
    blendamp_dir,
    save_comps,
    delete_existing,
    viscolor_path,
    pledit_path,
    text_comment,
    pixel_font_path,
):
    if viscolor_path is not None or pledit_path is not None:
        print(
            "Overriding base convert functionality to test pledit and viscolor conversions"
        )
        cli_textcolor_convert(viscolor_path, pledit_path)
        return
    if text_comment is not None:
        print(
            "Overriding base convert functionality to test text comment functionality"
        )
        with Image.open(pixel_font_path) as pixel_font_img:
            comment_img = pixel_font.write_pixel_comment(text_comment, pixel_font_img)
            comment_img.save(os.path.join(os.curdir, "test_comment.png"))
        return

    blendamp.convert(
        to_winamp,
        winamp_dir,
        blendamp_dir,
        save_comps,
        delete_existing,
    )
    return


if __name__ == "__main__":
    cli_convert()
