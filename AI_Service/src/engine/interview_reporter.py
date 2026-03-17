"""AI-powered final interview scorer and feedback generator."""

from __future__ import annotations

import json
import re
from typing import Any

from groq import Groq

from src.config import GROQ_API_KEY
from src.rag.retriever import retrieve_sops


MODEL_CANDIDATES = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]


def _parse_json_payload(raw_text: str) -> dict[str, Any]:
    try:
        return json.loads(raw_text)
    except Exception:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(raw_text[start : end + 1])


def _normalize_list(value: Any, max_items: int = 6) -> list[str]:
    if not isinstance(value, list):
        return []
    items = [str(item).strip() for item in value if str(item).strip()]
    return list(dict.fromkeys(items))[:max_items]


def _contains_any(text: str, patterns: list[str]) -> bool:
    lowered = (text or "").lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def _force_second_person(text: str) -> str:
    output = (text or "").strip()
    if not output:
        return output
    replacements = {
        r"\bthe candidate\b": "you",
        r"\bcandidate\b": "you",
        r"\bthe worker\b": "you",
        r"\bworker\b": "you",
        r"\bhe/she\b": "you",
        r"\bthey should\b": "you should",
        r"\bthey need to\b": "you need to",
    }
    for pattern, repl in replacements.items():
        output = re.sub(pattern, repl, output, flags=re.IGNORECASE)
    return output


def _heuristic_report(history: list[dict[str, Any]]) -> dict[str, Any]:
    total_turns = len(history)
    if total_turns == 0:
        return {
            "overall_score": 0,
            "result": "INCOMPLETE",
            "summary": "Assessment has no responses yet, so scoring could not be completed.",
            "feedback": "Please complete at least a few interview responses for an accurate evaluation.",
            "strengths": [],
            "improvements": ["Provide complete answers with practical steps and safety checks."],
        }

    answers = [(item.get("answer_en") or "").strip() for item in history]
    avg_words = sum(len(answer.split()) for answer in answers) / total_turns

    safety_hits = sum(
        1
        for answer in answers
        if _contains_any(answer, [r"\bsafety\b", r"\bppe\b", r"\binspect\b", r"\bverify\b", r"\blockout\b"])
    )
    step_hits = sum(
        1
        for answer in answers
        if _contains_any(answer, [r"\bfirst\b", r"\bthen\b", r"\bafter\b", r"\bfinally\b"])
    )
    vague_count = sum(1 for answer in answers if len(answer.split()) < 6)

    completion_factor = min(1.0, total_turns / 8)
    base = 38 + int(avg_words * 1.6) + (safety_hits * 3) + (step_hits * 2) + int(completion_factor * 18)
    score = max(15, min(94, base - vague_count * 6))
    result = "PASS" if score >= 60 else "FAIL"

    strengths: list[str] = []
    if safety_hits > 0:
        strengths.append("You referenced important safety checks in your responses.")
    if step_hits > 0:
        strengths.append("You attempted to explain work steps in sequence.")
    if avg_words >= 10:
        strengths.append("You provided reasonably detailed answers in multiple turns.")
    if not strengths:
        strengths.append("You stayed engaged and attempted to answer the interview questions.")

    improvements = [
        "Use concrete procedural steps instead of short generic replies.",
        "State safety checks explicitly before and after the task.",
    ]

    if result == "PASS":
        summary = f"Interview completed with practical understanding visible in multiple answers. Overall score: {score}/100."
        feedback = "You showed good progress. To improve further, keep adding explicit safety checks and verification steps in every response."
    else:
        summary = f"Interview responses show partial understanding but key trade details were often vague. Overall score: {score}/100."
        feedback = "Focus on step-by-step procedure, safety precautions, and final quality checks while answering."

    return {
        "overall_score": score,
        "result": result,
        "summary": _force_second_person(summary),
        "feedback": _force_second_person(feedback),
        "strengths": strengths,
        "improvements": improvements,
    }


def _build_sop_context(history: list[dict[str, Any]]) -> str:
    questions = []
    for item in history:
        q = (item.get("question_text") or "").strip()
        if q:
            questions.append(q)
    if not questions:
        return "General blue-collar SOP and safety compliance apply."

    unique_questions = list(dict.fromkeys(questions))[:3]
    chunks: list[str] = []
    for question in unique_questions:
        try:
            chunks.extend(retrieve_sops(question, top_k=2))
        except Exception:
            continue

    deduped = list(dict.fromkeys([chunk for chunk in chunks if chunk]))
    if not deduped:
        return "General blue-collar SOP and safety compliance apply."
    return "\n\n".join(deduped[:4])


def generate_final_interview_report(
    category_id: str,
    history: list[dict[str, Any]],
    total_primaries: int = 0,
    completed_primaries: int = 0,
) -> dict[str, Any]:
    """Return SOP-aware final report with score and feedback for completed interview."""

    if not GROQ_API_KEY:
        return _heuristic_report(history)

    client = Groq(api_key=GROQ_API_KEY)
    completion_ratio = 1.0 if total_primaries <= 0 else max(0.0, min(1.0, completed_primaries / total_primaries))
    sop_context = _build_sop_context(history)
    history_blob = "\n\n".join(
        [
            f"Question: {item.get('question_text', '')}\n"
            f"Answer: {item.get('answer_en', '')}\n"
            f"Turn Feedback: {item.get('evaluation', {}).get('feedback', '')}"
            for item in history
        ]
    )

    system_prompt = f"""
You are an expert vocational examiner evaluating a blue-collar interview.

Use this SOP context while judging the candidate:
{sop_context}

Return STRICT JSON only:
{{
  "overall_score": integer 0-100,
  "result": "PASS" | "FAIL" | "INCOMPLETE",
  "summary": "2-3 sentence final assessment summary",
  "feedback": "2-3 sentence practical improvement guidance",
  "strengths": ["string"],
  "improvements": ["string"]
}}

Scoring rules:
- Reward concrete steps, sequencing, safety awareness, and verification language.
- Penalize vague or very short responses.
- Use strict but fair grading for blue-collar practical readiness.
- Penalize incomplete interviews proportionally to unanswered primary questions.
- If interview is not completed, result must be "INCOMPLETE".
- Write summary and feedback directly to "you" (second person), never third person.
- Do not use generic praise like "willingness to learn" unless no other strength is available.
- Strengths and improvements should be specific and evidence-based.
""".strip()

    user_prompt = f"""
Category: {category_id}
Primary Questions Completed: {completed_primaries}/{total_primaries}

Interview History:
{history_blob}
""".strip()

    last_error: Exception | None = None
    for model_name in MODEL_CANDIDATES:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=420,
            )

            payload = _parse_json_payload(completion.choices[0].message.content.strip())
            score = int(payload.get("overall_score", 0))
            score = max(0, min(100, score))
            # Apply deterministic incompleteness penalty regardless of model output.
            score = int(round(score * (0.35 + 0.65 * completion_ratio)))
            result = str(payload.get("result", "INCOMPLETE")).upper().strip()
            if result not in {"PASS", "FAIL", "INCOMPLETE"}:
                result = "PASS" if score >= 60 else "FAIL"
            if completion_ratio < 1.0:
                result = "INCOMPLETE"

            summary = _force_second_person(str(payload.get("summary", "")).strip() or "Interview completed.")
            feedback = _force_second_person(str(payload.get("feedback", "")).strip() or summary)

            strengths = _normalize_list(payload.get("strengths"))
            if not strengths:
                strengths = _heuristic_report(history).get("strengths", [])

            improvements = _normalize_list(payload.get("improvements"))
            if not improvements:
                improvements = _heuristic_report(history).get("improvements", [])

            return {
                "overall_score": score,
                "result": result,
                "summary": summary,
                "feedback": feedback,
                "strengths": strengths,
                "improvements": improvements,
            }
        except Exception as exc:
            last_error = exc

    report = _heuristic_report(history)
    if completion_ratio < 1.0:
        report["overall_score"] = int(round(report["overall_score"] * (0.35 + 0.65 * completion_ratio)))
        report["result"] = "INCOMPLETE"
        report["summary"] = (
            f"{report['summary']} You completed {completed_primaries}/{total_primaries} primary questions."
        )
    if last_error:
        report["summary"] = f"{report['summary']} (AI fallback mode used.)"
    return report
