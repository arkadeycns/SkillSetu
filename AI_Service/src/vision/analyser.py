"""Vision + language competency evaluator for vocational assessments."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY

MODEL_NAME = "gemini-1.5-flash"


def _normalize_result(data: Dict[str, Any]) -> Dict[str, Any]:
    pass_fail = bool(data.get("pass_fail", False))
    feedback = str(data.get("feedback", "")).strip()

    raw_gaps = data.get("identified_gaps", [])
    if isinstance(raw_gaps, list):
        identified_gaps = [str(item).strip() for item in raw_gaps if str(item).strip()]
    else:
        identified_gaps = []

    return {
        "pass_fail": pass_fail,
        "feedback": feedback,
        "identified_gaps": identified_gaps,
    }


def evaluate_competency(image_path: str, user_transcript: str, sop_context: str) -> Dict[str, Any]:
    """
    Evaluate practical competency using image evidence, transcript, and SOP context.
    Returns dict with keys: pass_fail, feedback, identified_gaps.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY in environment.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    uploaded_image = client.files.upload(file=image_path)
    prompt = f"""
You are an expert vocational skill assessor for India-focused workforce training.
Evaluate the candidate using:
1) Image evidence from the work scenario.
2) Candidate verbal response transcript.
3) Gold-standard SOP context.

Your task:
- Decide if candidate is competent enough to pass this scenario.
- Give concise, practical, worker-friendly feedback.
- Identify specific missed steps or safety/quality gaps.

Return STRICT JSON only with this schema:
{{
  "pass_fail": boolean,
  "feedback": string,
  "identified_gaps": string[]
}}

Candidate transcript:
{user_transcript}

SOP context:
{sop_context}
""".strip()
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[uploaded_image, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2),
        )

        raw_text = (response.text or "").strip()
        if not raw_text:
            raise ValueError("Vision analyzer returned empty response.")

        parsed = json.loads(raw_text)
        if not isinstance(parsed, dict):
            raise ValueError("Vision analyzer response is not a JSON object.")

        return _normalize_result(parsed)
    finally:
        # Best-effort cleanup of uploaded file resource from Gemini File API.
        try:
            client.files.delete(name=uploaded_image.name)
        except Exception:
            pass