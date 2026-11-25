
from app.ocr_modules.ocr_api import extract_text_with_api


def extract_text(image_bytes, mime_type="image/jpeg"):

    return extract_text_with_api(
        image_bytes,
        mime_type
    )
