def _as_list(value):
    """Normalize model output into a list of readable strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def build_document_assessment(vision, ocr):
    """
    Convert Vision AI and OCR outputs into a user-friendly assessment.

    OpenCV measurements are intentionally not thresholded here: ELA, noise,
    edge count and ORB keypoints are not standalone evidence of tampering.
    """
    vision = vision if isinstance(vision, dict) else {}
    ocr = ocr if isinstance(ocr, dict) else {}

    model_status = str(vision.get("model_status", "unavailable")).lower()
    assessment = str(vision.get("assessment", "inconclusive")).lower()
    risk_level = str(vision.get("risk_level", "unknown")).lower()

    visual_observations = _as_list(vision.get("visual_observations"))
    suspicious_regions = _as_list(vision.get("suspicious_regions"))
    model_recommendations = _as_list(vision.get("recommendations"))
    limitations = _as_list(vision.get("limitations"))

    consistency = ocr.get("consistency_check", {})
    if not isinstance(consistency, dict):
        consistency = {}

    ocr_status = str(ocr.get("status", "unavailable")).lower()
    ocr_issues = _as_list(consistency.get("issues"))

    # Missing fields usually mean OCR could not read them; they are not proof
    # that somebody edited the document.
    missing_fields = [
        issue for issue in ocr_issues
        if issue.lower().startswith("missing field:")
    ]
    substantive_ocr_issues = [
        issue for issue in ocr_issues
        if not issue.lower().startswith("missing field:")
    ]

    suspicious_assessment = any(
        word in assessment
        for word in ("tamper", "forg", "manipulat", "altered", "suspicious")
    )
    clear_assessment = assessment in {
        "no_obvious_issue",
        "no_obvious_issues",
        "no_visible_issue",
        "no_visible_issues"
    }

    reasons = []

    if suspicious_assessment:
        reasons.extend(suspicious_regions or visual_observations)
        if not reasons:
            reasons.append(
                "The visual analysis identified signs that may indicate "
                "editing or alteration."
            )
    elif visual_observations:
        reasons.extend(visual_observations)

    if substantive_ocr_issues:
        reasons.extend(
            f"Invoice information check: {issue}"
            for issue in substantive_ocr_issues
        )

    if missing_fields:
        field_names = [
            issue.split(":", 1)[1].strip().replace("_", " ")
            for issue in missing_fields
        ]
        reasons.append(
            "Some invoice details could not be read clearly: "
            + ", ".join(field_names)
            + ". This may be an OCR limitation, not evidence of tampering."
        )

    if not reasons:
        reasons.append(
            "The automated checks did not return enough specific evidence "
            "to explain a possible alteration."
        )

    # A positive tampering assessment requires an explicit visual warning
    # from the vision model or substantive OCR inconsistencies.
    if model_status != "success":
        status = "inconclusive"
        title = "Unable to Complete Verification"
        summary = (
            "The visual AI check was unavailable, so KAVACH cannot provide "
            "a reliable document assessment."
        )
    elif suspicious_assessment or (
        risk_level == "high" and bool(suspicious_regions)
    ):
        status = "potentially_tampered"
        title = "Potential Signs of Manipulation"
        summary = (
            "The visual analysis found features that may indicate that "
            "part of this document has been changed. Verify the flagged "
            "details before accepting it."
        )
    elif substantive_ocr_issues:
        status = "needs_review"
        title = "Document Details Need Verification"
        summary = (
            "Some invoice details failed basic consistency checks. "
            "This does not by itself prove image tampering."
        )
    elif clear_assessment and ocr_status == "success":
        status = "no_obvious_tampering_detected"
        title = "No Obvious Manipulation Detected"
        summary = (
            "The visual AI check did not identify obvious signs of editing, "
            "and the readable invoice fields passed the available basic "
            "consistency checks. This does not prove the document is genuine."
        )
    else:
        status = "needs_review"
        title = "Further Verification Recommended"
        summary = (
            "The available checks are not sufficient to confidently assess "
            "this document. Some verification steps may be incomplete."
        )

    if status == "potentially_tampered":
        recommendations = [
            "Do not approve or make payment using this document until it is checked.",
            "Compare the flagged area with the original document received from the issuer.",
            "Confirm the invoice number, date, total amount and bank details with the issuing organization using independently verified contact details."
        ]
    elif status == "no_obvious_tampering_detected":
        recommendations = [
            "Cross-check the invoice number, amount and payment details with your purchase order or accounting records.",
            "Confirm the invoice with the issuing organization before making high-value payments."
        ]
    elif status == "inconclusive":
        recommendations = [
            "Retry the analysis when the Vision AI service is available.",
            "Upload a clear, complete image of the original document.",
            "Verify the invoice directly with the issuing organization before accepting it."
        ]
    else:
        recommendations = [
            "Check the invoice details listed above against the original records.",
            "Upload a clearer image if some text could not be read.",
            "Contact the issuing organization to confirm any inconsistent details."
        ]

    recommendations.extend(model_recommendations[:2])

    return {
        "status": status,
        "title": title,
        "summary": summary,
        "reasons": reasons[:8],
        "recommendations": recommendations[:6],
        "risk_level": risk_level,
        "limitations": limitations[:4],
        "disclaimer": (
            "AI-assisted findings are indicative, not proof of authenticity. "
            "Verify important documents with the issuing organization."
        )
    }
