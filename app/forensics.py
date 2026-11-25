
import cv2
import numpy as np
import io

from PIL import Image, ImageChops, ImageEnhance


def analyze_invoice(image_bytes):

    # Decode uploaded image
    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    # Convert to OpenCV format
    image_array = np.array(image)

    image_bgr = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2BGR
    )

    gray = cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2GRAY
    )

    # -------------------------
    # 1. ELA ANALYSIS
    # -------------------------

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=90
    )

    buffer.seek(0)

    compressed = Image.open(buffer).convert("RGB")

    difference = ImageChops.difference(
        image,
        compressed
    )

    ela = ImageEnhance.Brightness(
        difference
    ).enhance(15)

    ela_array = np.array(ela)

    ela_mean = float(np.mean(ela_array))

    # -------------------------
    # 2. NOISE RESIDUAL
    # -------------------------

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    noise = cv2.absdiff(
        gray,
        blurred
    )

    noise_mean = float(np.mean(noise))

    # -------------------------
    # 3. EDGE ANALYSIS
    # -------------------------

    edges = cv2.Canny(
        gray,
        100,
        200
    )

    edge_pixels = int(
        np.count_nonzero(edges)
    )

    # -------------------------
    # 4. ORB ANALYSIS
    # -------------------------

    orb = cv2.ORB_create(nfeatures=1500)

    keypoints, descriptors = orb.detectAndCompute(
        gray,
        None
    )

    keypoint_count = len(keypoints)

    # Return forensic measurements
    return {
        "image_width": image.width,
        "image_height": image.height,

        "ela_mean": round(ela_mean, 4),
        "noise_mean": round(noise_mean, 4),
        "edge_pixels": edge_pixels,
        "orb_keypoints": keypoint_count,

        "note": (
            "These are forensic measurements, "
            "not standalone proof of manipulation."
        )
    }
