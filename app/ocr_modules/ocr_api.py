
import os
import requests

from dotenv import load_dotenv

load_dotenv()

OCR_SPACE_URL = "https://api.ocr.space/parse/image"


def extract_text_with_api(image_bytes, mime_type="image/jpeg"):

    api_key = os.getenv("OCR_SPACE_API_KEY")

    if not api_key:
        raise RuntimeError("OCR_SPACE_API_KEY is missing")

    headers = {
        "apikey": api_key
    }

    extension = "png" if mime_type == "image/png" else "jpg"

    files = {
        "file": (f"invoice.{extension}", image_bytes, mime_type)
    }

    data = {
        "language": "eng",
        "OCREngine": 2,
        "isTable": True,
        "scale": True,
        "filetype": "PNG" if mime_type == "image/png" else "JPG"
    }

    try:
        response = requests.post(
            OCR_SPACE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=90
        )

        response.raise_for_status()
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            raise RuntimeError(
                str(result.get("ErrorMessage", "OCR processing failed"))
            )

        text_lines = []

        for page in result.get("ParsedResults", []):
            extracted_text = page.get("ParsedText", "")

            for line in extracted_text.splitlines():
                line = line.strip()

                if line:
                    text_lines.append(line)

        if not text_lines:
            raise RuntimeError("OCR returned no readable text")

        return text_lines

    except requests.RequestException as e:
        print("OCR.space API error:", str(e))
        raise RuntimeError("OCR.space request failed") from e
