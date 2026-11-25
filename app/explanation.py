
def generate_explanation(cnn, opencv):

    reasons = []
    recommendations = []

    # CNN interpretation
    authentic = cnn["authentic_score"]
    tampered = cnn["tampered_score"]

    score_gap = abs(authentic - tampered)

    if score_gap < 0.10:
        decision = "Inconclusive"
        reasons.append(
            "The CNN scores for Authentic and Tampered "
            "are very close. The model cannot confidently "
            "distinguish the document."
        )
    else:
        decision = "Requires Manual Review"
        reasons.append(
            f"The CNN currently leans towards "
            f"{cnn['prediction']}, but this model is experimental "
            "and its classification is not yet reliable."
        )

    # OpenCV measurements
    reasons.append(
        f"ELA analysis produced a mean difference value of "
        f"{opencv['ela_mean']}. This measurement needs "
        "reference-based interpretation."
    )

    reasons.append(
        f"Noise analysis produced a mean residual value of "
        f"{opencv['noise_mean']}. This alone does not establish tampering."
    )

    reasons.append(
        f"Edge analysis detected {opencv['edge_pixels']} edge pixels."
    )

    reasons.append(
        f"ORB extracted {opencv['orb_keypoints']} keypoints. "
        "This is feature information, not proof of manipulation."
    )

    # User recommendations
    recommendations.extend([
        "Verify the sender or issuing company's identity "
        "using independently obtained contact details.",

        "Cross-check invoice number, date, amount and bank "
        "account details with the purchase order or trusted records.",

        "If a previously registered blockchain hash exists, "
        "verify the uploaded document against that record.",

        "Request confirmation from the issuer before making payment."
    ])

    if decision == "Inconclusive":
        recommendations.insert(
            0,
            "Do not treat this result as proof that the invoice is authentic."
        )

    return {
        "decision": decision,
        "risk_assessment": "Undetermined",
        "reasons": reasons,
        "recommendations": recommendations,
        "model_limitation": (
            "CNN is experimental. OpenCV measurements are "
            "supporting forensic clues, not standalone proof."
        )
    }
