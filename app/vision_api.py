
import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            attempts=2,
            initial_delay=1,
            max_delay=3
        )
    )
)

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite"
]


def analyze_invoice_with_ai(image_bytes, mime_type):

    prompt = """
    You are analyzing a business invoice for possible visual
    manipulation.

    Examine:
    1. Inconsistent fonts and text alignment.
    2. Overwritten or altered amounts and dates.
    3. Unusual spacing and background differences.
    4. Suspicious image regions.
    5. Other visible document inconsistencies.

    Do not claim that a document is forged without evidence.
    A normal-looking image does not prove authenticity.
    If uncertain, return an inconclusive assessment.

    Return only valid JSON with these fields:

    {
      "assessment": "no_obvious_issue",
      "risk_level": "low",
      "visual_observations": [],
      "suspicious_regions": [],
      "recommendations": [],
      "limitations": []
    }
    """

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    for model_name in MODELS:

        try:
            print(f"Trying Vision API model: {model_name}")

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    prompt,
                    image_part
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)

            result["model_status"] = "success"
            result["model_used"] = model_name

            return result

        except errors.ServerError as e:

            print(f"{model_name} server error: {e}")

            if e.code in (500, 502, 503, 504):
                continue

            break

        except errors.APIError as e:

            print(f"Gemini API error: {e}")
            break

        except (json.JSONDecodeError, TypeError) as e:

            print(f"Invalid Gemini response: {e}")
            break

    return {
        "assessment": "inconclusive",
        "risk_level": "unknown",
        "visual_observations": [],
        "suspicious_regions": [],
        "recommendations": [
            "Vision AI was unavailable. Retry the analysis.",
            "Review the invoice manually."
        ],
        "limitations": [
            "No successful Vision AI analysis was obtained."
        ],
        "model_status": "unavailable"
    }
