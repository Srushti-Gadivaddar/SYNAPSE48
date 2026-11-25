
from app.ocr_modules.ocr_engine import extract_text
from app.ocr_modules.field_extractor import extract_fields
from app.ocr_modules.consistency_checker import check_consistency


def analyze_invoice_ocr(image_bytes, mime_type="image/jpeg"):

    try:
        # Extract invoice text
        text_lines = extract_text(
            image_bytes,
            mime_type
        )

        # Extract invoice fields
        fields = extract_fields(text_lines)

        # Verify field consistency
        issues = check_consistency(fields)

        return {
            "status": "success",
            "extracted_text": text_lines,
            "extracted_fields": fields,
            "consistency_check": {
                "passed": len(issues) == 0,
                "issues": issues
            }
        }

    except Exception as e:

        print("OCR service error:", str(e))

        return {
            "status": "unavailable",
            "extracted_text": [],
            "extracted_fields": {},
            "consistency_check": {
                "passed": False,
                "issues": [
                    "OCR verification could not be completed."
                ]
            },
            "error": "OCR API unavailable"
        }
