from pathlib import Path
from ocr_engine import extract_text
from field_extractor import extract_fields

BASE_DIR = Path(__file__).resolve().parent.parent

original_path = BASE_DIR / "blockchain" / "dataset" / "gst_certificates" / "original" / "invoice_0001_original.png"
manipulated_path = BASE_DIR / "blockchain" / "dataset" / "gst_certificates" / "manipulated" / "invoice_0001_manipulated.png"

print("Processing ORIGINAL document...")
original_fields = extract_fields(extract_text(str(original_path)))

print("\nProcessing MANIPULATED document...")
manipulated_fields = extract_fields(extract_text(str(manipulated_path)))


# Compare fields
matched_fields = []
changed_fields = []

for field in original_fields:
    original_value = original_fields.get(field)
    manipulated_value = manipulated_fields.get(field)

    if original_value == manipulated_value:
        matched_fields.append(field)
    else:
        changed_fields.append(field)


# Risk score
total_fields = len(original_fields)

if total_fields > 0:
    risk_score = (len(changed_fields) / total_fields) * 100
else:
    risk_score = 0


# Final report
print("\n" + "=" * 45)
print("       KAVACH DOCUMENT ANALYSIS")
print("=" * 45)

print(f"\nFields Compared : {total_fields}")
print(f"Fields Matched : {len(matched_fields)}")
print(f"Fields Changed : {len(changed_fields)}")

if changed_fields:
    print("\nChanged Fields:")
    for i, field in enumerate(changed_fields, start=1):
        print(f"  {i}. {field.replace('_', ' ').title()}")
else:
    print("\nNo field differences detected.")

print(f"\nRisk Score: {risk_score:.2f}%")

if risk_score == 0:
    print("Status: NO DIFFERENCES DETECTED")
else:
    print("Status: SUSPICIOUS - MANUAL REVIEW REQUIRED")

print("=" * 45)