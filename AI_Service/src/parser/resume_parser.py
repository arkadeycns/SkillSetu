from __future__ import annotations

import json
import re
from typing import Any

from groq import Groq

from src.config import GROQ_API_KEY


MODEL_CANDIDATES = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]

TRADE_SKILL_KEYWORDS = [
    "welding",
    "mig",
    "tig",
    "arc welding",
    "fabrication",
    "plumbing",
    "cpvc",
    "ppr",
    "electrical wiring",
    "panel board",
    "conduit",
    "switchgear",
    "maintenance",
    "preventive maintenance",
    "breakdown maintenance",
    "hvac",
    "refrigeration",
    "machine operation",
    "cnc",
    "lathe",
    "forklift",
    "warehouse",
    "inventory",
    "packing",
    "scaffolding",
    "masonry",
    "carpentry",
    "painting",
    "quality inspection",
    "safety",
    "ppe",
]


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if len(digits) < 10:
        return None
    if len(digits) == 10:
        return digits
    # Preserve country code if present.
    return f"+{digits}"


def extract_email(text: str) -> str | None:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = re.search(r"(?:\+?\d[\d\s().-]{8,}\d)", text)
    return _normalize_phone(match.group(0)) if match else None


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = [skill for skill in TRADE_SKILL_KEYWORDS if skill in text_lower]
    return list(dict.fromkeys(found))


def _estimate_experience_level(text: str) -> str:
    years = [int(y) for y in re.findall(r"(\d+)\+?\s*(?:years|yrs|year)", text.lower())]
    if not years:
        return "Unknown"
    top = max(years)
    if top <= 1:
        return "Entry-Level (0-1 years)"
    if top <= 3:
        return "Mid-Level (2-3 years)"
    if top <= 7:
        return "Experienced (4-7 years)"
    return "Senior (8+ years)"


def _parse_json_payload(raw_text: str) -> dict[str, Any]:
    try:
        return json.loads(raw_text)
    except Exception:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(raw_text[start : end + 1])


def _normalize_list(value: Any, max_items: int = 12) -> list[str]:
    if not isinstance(value, list):
        return []
    items = [_safe_text(v) for v in value]
    items = [v for v in items if v]
    return list(dict.fromkeys(items))[:max_items]


def _heuristic_parse(text: str) -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = lines[0] if lines else None
    if name and any(token in name.lower() for token in ["resume", "curriculum vitae", "cv"]):
        name = None

    skills = extract_skills(text)
    experience_level = _estimate_experience_level(text)

    return {
        "name": name,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": skills,
        "education": [],
        "experience": [],
        "role": "General Skilled Worker",
        "experience_level": experience_level,
        "confidence": "58%",
        "trade_roles": [],
        "certifications": [],
        "tools_machines": [],
        "safety_training": [],
        "preferred_shift": None,
        "preferred_locations": [],
        "languages": [],
        "strengths": [
            "Willingness to work in hands-on operational roles",
        ],
        "gaps": [
            "Limited structured evidence found for role-specific SOP depth",
        ],
        "recommended_training": [
            "Workplace safety and SOP adherence module",
        ],
        "blue_collar_report": {
            "fitment_summary": "Candidate profile suggests basic fit for blue-collar operations, pending practical trade validation.",
            "suitability_score": 55,
            "risk_flags": ["Incomplete structured resume details"],
            "next_best_roles": [],
        },
        "analysis_source": "rule_based_fallback",
        "parse_warning": None,
    }


def _ai_parse_resume(text: str) -> dict[str, Any]:
    if not GROQ_API_KEY:
        raise ValueError("Missing GROQ_API_KEY")

    client = Groq(api_key=GROQ_API_KEY)
    system_prompt = """
You are an expert Indian blue-collar recruitment analyst.
Extract and infer hiring-relevant details from raw resume text.

Return STRICT JSON only (no markdown) with this schema:
{
  "name": "string|null",
  "email": "string|null",
  "phone": "string|null",
  "skills": ["string"],
  "education": ["string"],
  "experience": ["string"],
  "role": "string",
  "experience_level": "string",
  "confidence": "string (0-100%)",
  "trade_roles": ["string"],
  "certifications": ["string"],
  "tools_machines": ["string"],
  "safety_training": ["string"],
  "preferred_shift": "string|null",
  "preferred_locations": ["string"],
  "languages": ["string"],
  "strengths": ["string"],
  "gaps": ["string"],
  "recommended_training": ["string"],
  "blue_collar_report": {
    "fitment_summary": "string",
    "suitability_score": "integer 0-100",
    "risk_flags": ["string"],
    "next_best_roles": ["string"]
  }
}

Guidelines:
- Prioritize trades: electrician, welder, fitter, plumber, machine operator, technician, warehouse roles.
- Infer only when strongly implied by evidence.
- Keep items concise and practical for recruiters.
""".strip()

    user_prompt = f"Resume text:\n{text[:16000]}"

    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=900,
            )
            raw = _safe_text(completion.choices[0].message.content)
            parsed = _parse_json_payload(raw)
            if not isinstance(parsed, dict):
                raise ValueError("AI response is not a JSON object")
            parsed["analysis_source"] = "ai"
            parsed["parse_warning"] = None
            return parsed
        except Exception as exc:
            last_error = exc

    raise ValueError(f"AI parsing failed: {last_error}")


def _normalize_output(data: dict[str, Any], text: str) -> dict[str, Any]:
    fallback_email = extract_email(text)
    fallback_phone = extract_phone(text)
    fallback_skills = extract_skills(text)

    blue_report = data.get("blue_collar_report", {})
    if not isinstance(blue_report, dict):
        blue_report = {}

    suitability = blue_report.get("suitability_score", 50)
    try:
        suitability_score = max(0, min(100, int(suitability)))
    except Exception:
        suitability_score = 50

    confidence = _safe_text(data.get("confidence"))
    if not re.match(r"^\d{1,3}%$", confidence):
        confidence = "65%"

    normalized = {
        "name": _safe_text(data.get("name")) or None,
        "email": _safe_text(data.get("email")) or fallback_email,
        "phone": _normalize_phone(_safe_text(data.get("phone"))) or fallback_phone,
        "skills": _normalize_list(data.get("skills"), max_items=20) or fallback_skills,
        "education": _normalize_list(data.get("education"), max_items=10),
        "experience": _normalize_list(data.get("experience"), max_items=12),
        "role": _safe_text(data.get("role")) or "General Skilled Worker",
        "experience_level": _safe_text(data.get("experience_level")) or _estimate_experience_level(text),
        "confidence": confidence,
        "trade_roles": _normalize_list(data.get("trade_roles"), max_items=8),
        "certifications": _normalize_list(data.get("certifications"), max_items=10),
        "tools_machines": _normalize_list(data.get("tools_machines"), max_items=14),
        "safety_training": _normalize_list(data.get("safety_training"), max_items=8),
        "preferred_shift": _safe_text(data.get("preferred_shift")) or None,
        "preferred_locations": _normalize_list(data.get("preferred_locations"), max_items=8),
        "languages": _normalize_list(data.get("languages"), max_items=8),
        "strengths": _normalize_list(data.get("strengths"), max_items=8),
        "gaps": _normalize_list(data.get("gaps"), max_items=8),
        "recommended_training": _normalize_list(data.get("recommended_training"), max_items=8),
        "blue_collar_report": {
            "fitment_summary": _safe_text(blue_report.get("fitment_summary"))
            or "Profile analyzed for blue-collar hiring fit.",
            "suitability_score": suitability_score,
            "risk_flags": _normalize_list(blue_report.get("risk_flags"), max_items=6),
            "next_best_roles": _normalize_list(blue_report.get("next_best_roles"), max_items=6),
        },
        "analysis_source": _safe_text(data.get("analysis_source")) or "ai",
        "parse_warning": data.get("parse_warning"),
    }
    return normalized


def parse_resume(text: str) -> dict[str, Any]:
    text = _safe_text(text)
    if not text:
        return _normalize_output(_heuristic_parse(""), "")

    try:
        ai_data = _ai_parse_resume(text)
        return _normalize_output(ai_data, text)
    except Exception as exc:
        fallback = _heuristic_parse(text)
        fallback["parse_warning"] = str(exc)
        return _normalize_output(fallback, text)