
from datetime import datetime
import re

def check_consistency(fields):
    issues = []

    # 1. Check missing important fields
    required_fields = [
        "supplier",
        "invoice_number",
        "buyer",
        "invoice_date",
        "total_amount"
    ]

    for field in required_fields:
        if not fields.get(field):
            issues.append(f"Missing field: {field}")

    # 2. Check invoice date format
    date_value = fields.get("invoice_date")

    if date_value:
        try:
            datetime.strptime(date_value, "%d/%m/%Y")
        except ValueError:
            issues.append("Invalid invoice date format")

    # 3. Validate GSTIN format if available
    gstin = fields.get("gstin")

    if gstin:
        gstin_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z][Z][0-9A-Z]$"

        if not re.match(gstin_pattern, gstin):
            issues.append("Invalid GSTIN format")

    # 4. Check invoice total
    total = fields.get("total_amount")

    if total:
        numeric_total = re.sub(r"[^0-9.]", "", total)

        try:
            if float(numeric_total) <= 0:
                issues.append("Invoice total must be greater than zero")
        except ValueError:
            issues.append("Invoice total is not a valid number")

    return issues


if __name__ == "__main__":
    from ocr_engine import extract_text
    from field_extractor import extract_fields

    image_path = input("Enter document image path: ")

    text_lines = extract_text(image_path)
    fields = extract_fields(text_lines)

    issues = check_consistency(fields)

    print("\n========== CONSISTENCY CHECK ==========\n")

    if issues:
        print("DOCUMENT FLAGGED")
        for issue in issues:
            print("-", issue)
    else:
        print("DOCUMENT PASSED BASIC CHECKS")
