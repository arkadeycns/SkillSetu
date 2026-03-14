"""Generate adaptive counter questions from SOP guidance and detected gaps."""

from __future__ import annotations

import json
from typing import List

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY

MODEL_NAME = "gemini-1.5-flash"


def generate_counter_questions(
    primary_question: str,
    user_answer_en: str,
    identified_gaps: List[str],
    sop_context: str,
    count: int = 2,
    previous_questions: List[str] | None = None,
) -> List[str]:
    """Generate exactly `count` non-repetitive counter questions in English."""
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY in environment.")

    previous = previous_questions or []

    prompt = f"""
You are creating short follow-up interview questions for vocational skill assessment.
Use SOP context for probing strategy. Do not repeat previously asked counters.

Rules:
- Return exactly {count} counter questions.
- Each question must target a missed step/safety gap.
- Keep each question under 20 words.
- Keep language simple and practical for blue-collar workers.
- Output must be STRICT JSON with key `counter_questions` (array of strings).

Primary question:
{primary_question}

Candidate answer:
{user_answer_en}

Identified gaps:
{json.dumps(identified_gaps, ensure_ascii=True)}

Previously asked counters:
{json.dumps(previous, ensure_ascii=True)}

SOP context:
{sop_context}
""".strip()

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2),
    )

    raw = (response.text or "").strip()
    if not raw:
        raise ValueError("Counter question generator returned an empty response.")

    parsed = json.loads(raw)
    questions = parsed.get("counter_questions", []) if isinstance(parsed, dict) else []
    cleaned = [str(item).strip() for item in questions if str(item).strip()]

    # Force exact count with deterministic fallbacks if model under-returns.
    fallback_pool = [
        "What safety step did you miss before starting this task?",
        "How would you verify quality before final handover?",
    ]
    for fallback in fallback_pool:
        if len(cleaned) >= count:
            break
        if fallback not in cleaned and fallback not in previous:
            cleaned.append(fallback)

    return cleaned[:count]
