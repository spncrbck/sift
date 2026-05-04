from PIL import Image
import io


MAX_WIDTH = 1400


def optimize_for_ocr(image_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(image_bytes))

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_size = (MAX_WIDTH, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Grayscale improves Tesseract accuracy
    img = img.convert("L")

    return img
