from statistics import quantiles
from PIL import Image
import uuid

from lib.utils import calc_percentage


def lower_image_quality(image_dir, q, p):
    image = Image.open(image_dir)
    new_size = (calc_percentage(image.size[0], p), calc_percentage(image.size[1], p))
    resized_image = image.resize(new_size, Image.NONE)
    final = resized_image.resize(image.size)
    final = final.resize(new_size, Image.NONE)
    final = final.resize(image.size)
    path = f"cache/{uuid.uuid4()}.jpg"
    final.save(path, quality=q)
    return path