import io
from typing import List
from PIL import Image


def stitch_images(images_as_bytes: List[bytes], rows_cols: int = 3) -> io.BytesIO:
    """https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array

    Args:
        images_as_bytes (List[bytes])

    Returns:
        io.BytesIO
    """
    images = [Image.open(i) for i in images_as_bytes]
    w, h = images[0].size
    grid = Image.new("RGB", size=(rows_cols * w, rows_cols * h))

    for idx, img in enumerate(images):
        grid.paste(img, box=(idx % rows_cols * w, idx // rows_cols * h))

    ret = io.BytesIO()
    grid.save(ret, "PNG")

    ret.seek(0)
    return ret
