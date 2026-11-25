
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError

from app.forensics import analyze_invoice
from app.vision_api import analyze_invoice_with_ai
from app.ocr_modules.ocr_service import analyze_invoice_ocr

app = FastAPI(
    title="KAVACH API",
    description="AI-powered Business Document Forgery Detection",
    version="1.0"
)


@app.get("/")
def home():
    return {
        "project": "KAVACH",
        "status": "running"
    }


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
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded"
        )

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 10 MB"
        )

    try:
        Image.open(BytesIO(image_bytes)).verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted image"
        )

    # 1. Gemini Vision analysis
    vision_result = analyze_invoice_with_ai(
        image_bytes,
        file.content_type
    )

    # 2. OpenCV forensic analysis
    try:
        opencv_result = analyze_invoice(image_bytes)
        opencv_status = "success"
    except Exception as e:
        print("OpenCV error:", str(e))
        opencv_result = {
            "error": "OpenCV analysis unavailable"
        }
        opencv_status = "unavailable"

    # 3. Mistral OCR and field consistency
    ocr_result = analyze_invoice_ocr(
        image_bytes,
        file.content_type
    )

    # 4. Return combined results
    return {
        "filename": file.filename,

        "vision_ai_analysis": vision_result,

        "opencv_analysis": opencv_result,

        "ocr_analysis": ocr_result,

        "component_status": {
            "vision_ai": vision_result.get(
                "model_status", "success"
            ),
            "opencv": opencv_status,
            "ocr": ocr_result.get("status", "unknown")
        },

        "overall_status": "needs_manual_review",

        "message": (
            "This result contains automated indicators. "
            "It is not a guarantee of document authenticity."
        )
    }
