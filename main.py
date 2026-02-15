from PIL import Image
from PIL.ImageFile import ImageFile as ImageFile

im: ImageFile = Image.open("test_baselayer.png")

subsct_img = im.crop((0, 0, im.size[0] - 1, (im.size[1] / 2) - 1))
subsct_img.convert("RGB").save("out.jpg")

im.close()
