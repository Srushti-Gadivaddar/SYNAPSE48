
import re

def extract_fields(text_lines):
    full_text = "\n".join(text_lines)

    fields = {
        "supplier": text_lines[0] if text_lines else None,
        "invoice_number": None,
        "buyer": None,
        "invoice_date": None,
        "total_amount": None,
        "bank_account": None,
        "gstin": None
    }

    patterns = {
        "invoice_number": r"Invoice No:\s*([A-Z0-9\-]+)",
        "buyer": r"Bill To:\s*(.+)",
        "invoice_date": r"Invoice Date:\s*(\d{2}/\d{2}/\d{4})",
        "total_amount": r"Invoice Total:\s*([₹€$0-9,\.]+)",
        "bank_account": r"Bank Account:\s*(.+)",
        "gstin": r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z]\d{1,2}\b"
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, full_text, re.IGNORECASE)

        if match:
            if field == "gstin":
                fields[field] = match.group(0)
            else:
                fields[field] = match.group(1).strip()

    return fields


if __name__ == "__main__":
    from ocr_engine import extract_text

    image_path = input("Enter document image path: ")
    text_lines = extract_text(image_path)

    fields = extract_fields(text_lines)

    print("\n========== EXTRACTED FIELDS ==========\n")

    for field, value in fields.items():
        print(f"{field}: {value}")
