"""Prompt-driven interview turn workflow logic for assessment orchestration."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from groq import Groq

from src.config import GROQ_API_KEY
from src.rag.retriever import retrieve_sops


MODEL_CANDIDATES = [
    os.environ.get("GROQ_CHAT_MODEL", "llama-3.1-8b-instant").strip(),
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


def _parse_turn_payload(raw_text: str) -> dict[str, str]:
    text = (raw_text or "").strip()
    if not text:
        raise ValueError("Empty turn outcome response.")

    # Primary path: JSON object.
    try:
        payload = _parse_json_payload(text)
        next_step = str(payload.get("next_step", "")).strip().lower()
        feedback = str(payload.get("feedback", "")).strip()
        if next_step:
            return {"next_step": next_step, "feedback": feedback}
    except Exception:
        pass

    # Fallback path: line format.
    # NEXT_STEP: ask_counter
    # FEEDBACK: Your answer is clear.
    # USE_QA_FEEDBACK: true
    match_next = re.search(r"NEXT_STEP\s*:\s*(retry_primary|ask_counter|advance)", text, flags=re.IGNORECASE)
    match_feedback = re.search(r"FEEDBACK\s*:\s*(.+)", text, flags=re.IGNORECASE | re.DOTALL)
    match_use_qa = re.search(r"USE_QA_FEEDBACK\s*:\s*(true|false)", text, flags=re.IGNORECASE)

    if not match_next:
        raise ValueError("Could not parse NEXT_STEP from model response.")

    feedback = ""
    if match_feedback:
        feedback = match_feedback.group(1).strip()
        feedback = re.sub(r"\s+", " ", feedback)

    payload = {
        "next_step": match_next.group(1).lower(),
        "feedback": feedback,
    }
    if match_use_qa:
        payload["use_qa_feedback"] = match_use_qa.group(1).lower()
    return payload


def _normalize_question(text: str) -> str:
    base = (text or "").strip().lower()
    base = re.sub(r"[^a-z0-9\s]", "", base)
    base = re.sub(r"\s+", " ", base)
    return base


def decide_turn_outcome(
    question: str,
    answer_en: str,
    stage: str,
    retry_used: bool,
    counter_retry_used: bool = False,
    chat_history: List[Dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Return an AI decision for the next interview step."""

    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY for interview workflow decisions.")

    history_text = ""
    for item in (chat_history or []):
        history_text += f"Q: {item.get('question', '')}\nA: {item.get('answer_en', '')}\n"

    try:
        sop_chunks = retrieve_sops(question, top_k=3)
        sop_context = "\n\n".join(sop_chunks) if sop_chunks else "General safety SOP applies."
    except Exception:
        sop_context = "General safety SOP applies."

    client = Groq(api_key=GROQ_API_KEY)
    system_prompt = f"""
You are running a multi-turn vocational interview.
Use simple language and decide the next step from this fixed set:
- retry_primary
- ask_counter
- advance

Return ONLY in one of these formats:
1) JSON object with keys next_step, feedback, use_qa_feedback
2) Plain text with exactly three lines:
     NEXT_STEP: retry_primary|retry_counter|ask_counter|advance
   FEEDBACK: one short sentence to the learner
     USE_QA_FEEDBACK: true|false

Decision guidance:
- Explicit skip intent ("next", "skip", "pass", "I don't know", "no idea", "not sure"):
    set NEXT_STEP=advance and FEEDBACK="It's okay, let's move on to the next question." and USE_QA_FEEDBACK=false.
- Gibberish/unclear:
    if stage=primary and retry_used=false => NEXT_STEP=retry_primary, USE_QA_FEEDBACK=false.
    if stage=retry_primary => NEXT_STEP=advance, USE_QA_FEEDBACK=false.
    if stage in counter_1/counter_2 and counter_retry_used=false => NEXT_STEP=retry_counter, USE_QA_FEEDBACK=false.
    if stage in counter_1/counter_2 and counter_retry_used=true => NEXT_STEP=advance, USE_QA_FEEDBACK=false.
- Satisfactory main answer: NEXT_STEP=ask_counter and USE_QA_FEEDBACK=true.
- Unsatisfactory but understandable main answer: retry only once on primary, then advance.
- For counter answers, no unsatisfactory retries; only gibberish gets one retry.
- Keep FEEDBACK in second person and concise.

SOP context:
{sop_context}
""".strip()

    user_prompt = f"""
Stage: {stage}
Retry already used for this primary: {retry_used}

Conversation history:
{history_text}

Current question:
{question}

Worker answer:
{answer_en}
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
                temperature=0.1,
                max_tokens=260,
            )
            raw_text = (completion.choices[0].message.content or "").strip()
            if not raw_text:
                raise ValueError("Groq returned an empty decision response.")

            payload = _parse_turn_payload(raw_text)
            feedback = str(payload.get("feedback", "")).strip()
            if not feedback:
                feedback = "Please continue."

            next_step = str(payload.get("next_step", "")).strip().lower()
            if next_step not in {"retry_primary", "retry_counter", "ask_counter", "advance"}:
                raise ValueError(f"Invalid next_step from Groq: {next_step!r}")

            if not feedback:
                raise ValueError("Groq returned empty feedback in turn outcome.")

            use_qa_raw = str(payload.get("use_qa_feedback", "")).strip().lower()
            use_qa_feedback = use_qa_raw != "false"

            return {
                "next_step": next_step,
                "feedback": feedback,
                "use_qa_feedback": use_qa_feedback,
            }
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(f"Groq failed to decide interview turn outcome: {last_error}")


def generate_counters_for_primary(
    primary_question: str,
    answer_en: str,
    feedback: str,
    previous_questions: list[str],
    count: int = 2,
) -> list[str]:
    if count <= 0:
        return []

    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY for counter question generation.")

    try:
        sop_chunks = retrieve_sops(primary_question, top_k=2)
        sop_context = "\n\n".join(sop_chunks) if sop_chunks else "General safety SOP applies."
    except Exception:
        sop_context = "General safety SOP applies."
    previous_text = "\n".join(previous_questions) if previous_questions else "None"

    system_prompt = f"""
You are a practical interviewer.
Generate short follow-up questions only.
Avoid repeating previous follow-ups.
Return one question per line. No numbering.

SOP context:
{sop_context}
""".strip()

    user_prompt = f"""
Primary question:
{primary_question}

Learner answer:
{answer_en}

Feedback summary:
{feedback}

Previous follow-ups:
{previous_text}

Generate {count} follow-up questions.
""".strip()

    client = Groq(api_key=GROQ_API_KEY)
    raw = ""

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
                max_tokens=260,
            )
            raw = (completion.choices[0].message.content or "").strip()
            if raw:
                break
        except Exception as exc:
            last_error = exc
            continue

    if not raw:
        raise RuntimeError(f"Groq failed to generate counter questions: {last_error}")

    seen = {_normalize_question(primary_question)}
    seen.update(_normalize_question(item) for item in previous_questions if item)

    cleaned: list[str] = []
    for line in raw.splitlines():
        candidate = line.strip().lstrip("- ").strip()
        if not candidate:
            continue
        norm = _normalize_question(candidate)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        cleaned.append(candidate)
        if len(cleaned) >= count:
            break

    if len(cleaned) < count:
        raise RuntimeError(
            f"Model generated only {len(cleaned)} unique counter question(s); expected {count}."
        )

    return cleaned[:count]
