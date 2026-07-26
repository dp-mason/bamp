import yaml

from PIL import Image
from importlib import resources

# Open and read the YAML file
with resources.open_text("bamp", "winamp_skin_specification.yaml") as winamp_spec:
    TEXT_SPEC: dict = yaml.safe_load(winamp_spec)["text_extras"]
    winamp_spec.close()

CHAR_WIDTH = TEXT_SPEC["CHAR_WIDTH"]
CHAR_HEIGHT = TEXT_SPEC["CHAR_HEIGHT"]


# return a single line comment written in a pixel_font
def write_pixel_comment(msg: str, pixel_font: Image.Image) -> Image.Image:
    comment_img = Image.new(
        "RGB",
        (len(msg) * CHAR_WIDTH, CHAR_HEIGHT),
        color=(255, 0, 0),  # TODO: background color
    )

    currsor = (0, 0)  # top left pixel position of the current char position
    for curr_char in msg:
        char_region = TEXT_SPEC["CHAR_POSITIONS"][curr_char.upper()]
        comment_img.paste(
            pixel_font.crop(
                (
                    char_region[0],
                    char_region[1],
                    char_region[0] + CHAR_WIDTH,
                    char_region[1] + CHAR_HEIGHT,
                )
            ),
            currsor,
        )
        currsor = (currsor[0] + CHAR_WIDTH, 0)

    return comment_img
