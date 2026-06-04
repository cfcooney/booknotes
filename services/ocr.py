import base64
import io
import logging
import os

import requests
from PIL import Image

logger = logging.getLogger(__name__)

_API_URL = "https://vision.googleapis.com/v1/images:annotate"
_MAX_DIMENSION = 1600


def extract_text_from_image(image_path: str) -> str | None:
    api_key = os.environ.get("GOOGLE_VISION_API_KEY")
    if not api_key:
        logger.error("GOOGLE_VISION_API_KEY environment variable is not set")
        return None

    try:
        img = Image.open(image_path)

        # JPEG doesn't support alpha or palette modes
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        w, h = img.size
        if max(w, h) > _MAX_DIMENSION:
            scale = _MAX_DIMENSION / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        b64 = base64.b64encode(buf.getvalue()).decode()

        payload = {
            "requests": [
                {
                    "image": {"content": b64},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                }
            ]
        }
        resp = requests.post(f"{_API_URL}?key={api_key}", json=payload, timeout=30)
        resp.raise_for_status()

        data = resp.json()
        responses = data.get("responses", [])
        if responses:
            annotation = responses[0].get("fullTextAnnotation")
            if annotation:
                return annotation.get("text")
        return None

    except Exception:
        logger.exception("OCR failed for %s", image_path)
        return None


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2:
        print("Usage: python -m services.ocr <image_path>")
        sys.exit(1)
    text = extract_text_from_image(sys.argv[1])
    print(text if text else "(no text extracted)")
