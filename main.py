from PIL import Image
from PIL.ImageFile import ImageFile as ImageFile

import yaml

im: ImageFile = Image.open("test_baselayer.png")

subsct_img = im.crop((0, 0, im.size[0] - 1, (im.size[1] / 2) - 1))
subsct_img.convert("RGB").save("out.bmp")

im.close()

# Open and read the YAML file
with open("winamp_skin_specification.yaml", "r") as file:
    config = yaml.safe_load(file)
print(config)

start = config["winamp"]["cbuttons.bmp"]["prev_button_norm"]
# print(start)
print(start)
