
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError
from io import BytesIO

from app.model import predict_invoice
from app.forensics import analyze_invoice
from app.explanation import generate_explanation


app = FastAPI(
    title="KAVACH API",
    description="AI-powered Invoice Forensics",
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
        "cnn": "loaded",
        "opencv": "loaded"
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
        image = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

        # CNN prediction
        cnn_result = predict_invoice(image)

        # OpenCV analysis
        opencv_result = analyze_invoice(image_bytes)
        explanation = generate_explanation(
        cnn_result,
        opencv_result
    )

        return {
        "filename": file.filename,
        "cnn_analysis": cnn_result,
        "opencv_analysis": opencv_result,
        "explanation": explanation,
        "overall_status": "needs_manual_review"
    }

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Unable to process this image"
        )
