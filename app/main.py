from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError

from app.forensics import analyze_invoice
from app.vision_api import analyze_invoice_with_ai
from app.ocr_modules.ocr_service import analyze_invoice_ocr
from app.explanation import build_document_assessment

app = FastAPI(
    title="KAVACH API",
    description="AI-powered Business Document Forgery Detection",
    version="1.1"
)


@app.get("/")
def home():
    return {"project": "KAVACH", "status": "running"}


@app.get("/health")
def health():
    return {
        "api": "running",
        "vision_ai": "configured",
        "ocr_api": "configured",
        "opencv": "configured",
        "cnn": "not_used"
    }


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Upload JPG or PNG images only"
        )

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 10 MB"
        )

    try:
        image = Image.open(BytesIO(image_bytes))
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted image"
        )

    # 1. Gemini Vision: visual indicators of possible editing
    try:
        vision_result = analyze_invoice_with_ai(
            image_bytes,
            file.content_type
        )
    except Exception as exc:
        print("Vision AI error:", str(exc))
        vision_result = {
            "assessment": "inconclusive",
            "risk_level": "unknown",
            "visual_observations": [],
            "suspicious_regions": [],
            "recommendations": ["Retry the visual analysis later."],
            "limitations": ["Vision AI service was unavailable."],
            "model_status": "unavailable"
        }

    # 2. OpenCV: supporting image measurements, not a verdict
    try:
        opencv_result = analyze_invoice(image_bytes)
        opencv_status = "success"
    except Exception as exc:
        print("OpenCV error:", str(exc))
        opencv_result = {"error": "Image forensic analysis unavailable"}
        opencv_status = "unavailable"

    # 3. OCR: extracted invoice fields and basic consistency checks
    try:
        ocr_result = analyze_invoice_ocr(
            image_bytes,
            file.content_type
        )
    except Exception as exc:
        print("OCR error:", str(exc))
        ocr_result = {
            "status": "unavailable",
            "extracted_text": [],
            "extracted_fields": {},
            "consistency_check": {
                "passed": False,
                "issues": ["OCR verification could not be completed."]
            }
        }

    # 4. One understandable assessment for the extension/report
    assessment = build_document_assessment(
        vision_result,
        ocr_result
    )

    return {
        "filename": file.filename,
        "assessment": assessment,
        "overall_status": assessment["status"],
        "message": assessment["summary"],

        # Keep detailed component outputs available for the report
        "vision_ai_analysis": vision_result,
        "opencv_analysis": opencv_result,
        "ocr_analysis": ocr_result,

        "component_status": {
            "vision_ai": vision_result.get("model_status", "unknown"),
            "opencv": opencv_status,
            "ocr": ocr_result.get("status", "unknown")
        }
    }
