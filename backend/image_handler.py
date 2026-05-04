from PIL import Image, ImageFilter, ImageOps
import io


# Tesseract wants ~300 DPI. Screen screenshots are usually 96-144 DPI,
# so we upscale to get sharper character edges before thresholding.
TARGET_WIDTH = 2400
MIN_WIDTH = 1200


def optimize_for_ocr(image_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(image_bytes))

    if img.mode not in ("RGB", "RGBA", "L"):
        img = img.convert("RGB")
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg

    img = img.convert("L")

    # Upscale small/screen-res images so Tesseract has more pixels per character
    if img.width < TARGET_WIDTH:
        scale = TARGET_WIDTH / img.width
        img = img.resize(
            (int(img.width * scale), int(img.height * scale)),
            Image.LANCZOS,
        )
    elif img.width > TARGET_WIDTH * 1.5:
        # Very wide images — scale down to keep memory sane
        ratio = TARGET_WIDTH / img.width
        img = img.resize(
            (TARGET_WIDTH, int(img.height * ratio)),
            Image.LANCZOS,
        )

    # Sharpen slightly to help with aliased screen text
    img = img.filter(ImageFilter.SHARPEN)

    # Adaptive binarization: boosts contrast and removes background noise.
    # autocontrast stretches the histogram; then we threshold at midpoint.
    img = ImageOps.autocontrast(img, cutoff=2)

    return img
