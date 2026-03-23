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

ABUSE_PATTERNS = [
    r"\b(?:fuck|f\*+k|bc|mc|chutiya|madarchod|bhosdike|gaand|randi|harami|bastard|idiot|stupid)\b",
]

TECH_SIGNAL_PATTERNS = [
    r"\bsafety\b",
    r"\bppe\b",
    r"\binspect\b",
    r"\bverify\b",
    r"\btool\b",
    r"\bsequence\b",
    r"\bprocedure\b",
    r"\bmeasurement\b",
    r"\bdiagnos\w*\b",
    r"\bmaintenance\b",
]

GENERIC_STRENGTH_PATTERNS = [
    r"\bwillingness\b",
    r"\battitude\b",
    r"\bmotiv\w*\b",
    r"\bengaged\b",
    r"\btried\b",
    r"\bgood effort\b",
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


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _clamp_score(value: int) -> int:
    return max(1, min(100, int(value)))


def _contains_any(text: str, patterns: list[str]) -> bool:
    lowered = (text or "").lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def _technical_signal_count(history: list[dict[str, Any]]) -> int:
    count = 0
    for item in history:
        answer = str(item.get("answer_en") or "")
        if _is_abusive_answer(answer):
            continue
        if _contains_any(answer, TECH_SIGNAL_PATTERNS):
            count += 1
    return count


def _abusive_count(history: list[dict[str, Any]]) -> int:
    count = 0
    for item in history:
        eval_flag = item.get("evaluation", {}).get("is_abusive")
        if isinstance(eval_flag, bool):
            if eval_flag:
                count += 1
            continue
        answer = str(item.get("answer_en") or "").lower()
        if any(re.search(pattern, answer) for pattern in ABUSE_PATTERNS):
            count += 1
    return count


def _is_abusive_answer(text: str) -> bool:
    lowered = (text or "").lower()
    return any(re.search(pattern, lowered) for pattern in ABUSE_PATTERNS)


def _filter_technical_strengths(strengths: list[str], history: list[dict[str, Any]]) -> list[str]:
    if not strengths:
        return []

    non_abusive_answers = [
        str(item.get("answer_en") or "")
        for item in history
        if not _is_abusive_answer(str(item.get("answer_en") or ""))
    ]
    history_blob = " ".join(non_abusive_answers).lower()
    if not history_blob.strip():
        return []

    filtered: list[str] = []
    for strength in strengths:
        text = (strength or "").strip()
        if not text:
            continue
        lowered = text.lower()
        if any(re.search(pattern, lowered) for pattern in GENERIC_STRENGTH_PATTERNS):
            continue
        if not any(re.search(pattern, lowered) for pattern in TECH_SIGNAL_PATTERNS):
            continue
        # Require at least one technical cue also present in the answer history.
        if not any(re.search(pattern, history_blob) for pattern in TECH_SIGNAL_PATTERNS):
            continue
        filtered.append(text)
    return list(dict.fromkeys(filtered))[:6]


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
            "overall_score": 1,
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
    abusive_count = _abusive_count(history)
    technical_count = _technical_signal_count(history)

    completion_factor = min(1.0, total_turns / 8)
    base = 38 + int(avg_words * 1.6) + (safety_hits * 3) + (step_hits * 2) + int(completion_factor * 18)
    score = _clamp_score(max(0, min(94, base - vague_count * 6 - abusive_count * 18)))
    result = "PASS" if score >= 60 else "FAIL"

    strengths: list[str] = []
    if safety_hits > 0:
        strengths.append("You referenced important safety checks in your responses.")
    if step_hits > 0:
        strengths.append("You attempted to explain work steps in sequence.")
    if avg_words >= 10:
        strengths.append("You provided reasonably detailed answers in multiple turns.")
    strengths = _filter_technical_strengths(strengths, history)

    improvements = [
        "Use concrete procedural steps instead of short generic replies.",
        "State safety checks explicitly before and after the task.",
    ]

    if abusive_count > 0:
        improvements.insert(0, "Use respectful professional language; abusive words are unacceptable in assessment.")
        result = "FAIL"
        strengths = []

    abusive_ratio = abusive_count / max(1, total_turns)
    if abusive_ratio >= 0.5 and technical_count == 0:
        # Catastrophic interview quality: mostly abuse and no technical evidence.
        score = 1
        result = "FAIL"

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
    "completion_adjusted_score": integer 0-100,
  "result": "PASS" | "FAIL" | "INCOMPLETE",
  "summary": "2-3 sentence final assessment summary",
  "feedback": "2-3 sentence practical improvement guidance",
  "strengths": ["string"],
    "improvements": ["string"],
    "scoring_rationale": "1-2 sentence explanation of how score was decided"
}}

Scoring rules:
- Reward concrete steps, sequencing, safety awareness, and verification language.
- Penalize vague or very short responses.
- Use strict but fair grading for blue-collar practical readiness.
- Apply completion penalty directly in completion_adjusted_score.
- If interview is not completed, result must be "INCOMPLETE".
- Penalize abusive/profane language as professionalism failure.
- Write summary and feedback directly to "you" (second person), never third person.
- Do not use generic praise like "willingness to learn" unless no other strength is available.
- Strengths and improvements should be specific and evidence-based.
""".strip()

    user_prompt = f"""
Category: {category_id}
Primary Questions Completed: {completed_primaries}/{total_primaries}
Completion ratio: {completion_ratio:.2f}
Detected abusive answer turns: {_abusive_count(history)}

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
                max_tokens=520,
            )

            payload = _parse_json_payload(completion.choices[0].message.content.strip())
            score = _safe_int(payload.get("completion_adjusted_score"), _safe_int(payload.get("overall_score"), 1))
            score = _clamp_score(score)
            result = str(payload.get("result", "INCOMPLETE")).upper().strip()
            if result not in {"PASS", "FAIL", "INCOMPLETE"}:
                result = "PASS" if score >= 60 else "FAIL"
            if completion_ratio < 1.0:
                result = "INCOMPLETE"

            summary = _force_second_person(str(payload.get("summary", "")).strip() or "Interview completed.")
            feedback = _force_second_person(str(payload.get("feedback", "")).strip() or summary)

            strengths = _normalize_list(payload.get("strengths"))
            strengths = _filter_technical_strengths(strengths, history)
            if not strengths:
                strengths = _filter_technical_strengths(_heuristic_report(history).get("strengths", []), history)

            improvements = _normalize_list(payload.get("improvements"))
            if not improvements:
                improvements = _heuristic_report(history).get("improvements", [])

            abusive_count = _abusive_count(history)
            technical_count = _technical_signal_count(history)
            if abusive_count > 0:
                if "Use respectful professional language; abusive words are unacceptable in assessment." not in improvements:
                    improvements.insert(0, "Use respectful professional language; abusive words are unacceptable in assessment.")

                abusive_ratio = abusive_count / max(1, len(history))
                if abusive_ratio >= 0.25:
                    # Suppress strengths when abuse materially contaminates interview evidence.
                    strengths = []

                # Force near-minimum scores for abusive/no-technical interviews.
                if abusive_ratio >= 0.5 and technical_count == 0:
                    score = 1
                    result = "FAIL"
                elif abusive_ratio >= 0.25 and technical_count <= 1:
                    score = min(score, 5)
                    result = "FAIL"

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
        # Keep incompleteness penalty, but allow poor interviews to remain very low.
        report["overall_score"] = _clamp_score(int(round(report["overall_score"] * (0.1 + 0.9 * completion_ratio))))
        report["result"] = "INCOMPLETE"
        report["summary"] = (
            f"{report['summary']} You completed {completed_primaries}/{total_primaries} primary questions."
        )
    if last_error:
        report["summary"] = f"{report['summary']} (AI fallback mode used.)"
    return report
