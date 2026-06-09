from PIL import Image, ImageOps


def normalize_image(source_path: str, dest_path: str) -> None:
    """Apply EXIF orientation, convert to RGB, save as JPEG.

    Android camera JPEGs store rotation in EXIF metadata rather than
    rotating pixels. Without this step, the displayed image and the
    pixel data disagree, breaking crop coordinate math.
    """
    img = Image.open(source_path)
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    img.save(dest_path, "JPEG", quality=92)


def apply_crop(
    source_path: str, box: tuple[int, int, int, int], dest_path: str
) -> None:
    """Crop source_path to box and save as JPEG.

    box = (left, upper, right, lower) in image pixels, top-left origin (PIL convention).
    source_path should already be EXIF-normalized (see normalize_image).
    """
    img = Image.open(source_path)
    img.crop(box).save(dest_path, "JPEG", quality=92)
