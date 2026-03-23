"""Reusable AI helpers for chat and training recommendations."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from groq import Groq

from src.config import GROQ_API_KEY
from src.rag.qa import career_chat_query, rag_query


MODEL_CANDIDATES = [
    os.environ.get("GROQ_CHAT_MODEL", "llama-3.1-8b-instant").strip(),
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]

ABUSE_PATTERNS = [
    r"\b(?:fuck|f\*+k|bc|mc|chutiya|madarchod|bhosdike|gaand|randi|harami|bastard|idiot|stupid|moron|shut\s*up)\b",
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


def _has_explicit_abuse_markers(text: str) -> bool:
    lowered = (text or "").lower()
    return any(re.search(pattern, lowered) for pattern in ABUSE_PATTERNS)


def _guidance_turn_decision(
    message: str,
    history: List[Dict[str, str]],
    role: str,
    language: str,
) -> Dict[str, str]:
    """AI-first turn classifier for guidance chat.

    Returns dict with:
    - action: "abuse" | "clarify" | "answer"
    - assistant_reply: optional direct response for abuse/clarify actions
    """

    if not GROQ_API_KEY:
        return {"action": "answer", "assistant_reply": ""}

    history_text = ""
    for item in (history or [])[-8:]:
        history_text += f"User: {item.get('question', '')}\nAssistant: {item.get('answer_en', '')}\n"

    lang = (language or "en").strip().lower()
    lang_rule = "Reply in English."
    if lang in {"hi", "hindi", "hinglish", "hi-in"}:
        lang_rule = "Reply in natural Hinglish using only Latin script."

    system_prompt = f"""
You are the moderation and routing brain for a vocational guidance assistant.
Classify the user message and return STRICT JSON ONLY:
{{
  "action": "abuse" | "clarify" | "answer",
  "assistant_reply": "string"
}}

Rules:
- action=abuse if message contains abusive/profane/hostile language. assistant_reply must be a short warning only.
- action=clarify if message is mic-test/noise/empty/non-informative. assistant_reply must only say it could not understand and ask user to repeat clearly.
- action=answer for valid guidance requests; assistant_reply should be empty string.
- Keep assistant_reply concise (1-2 sentences), practical, professional, and role-aware for: {role}.
- Do not use slang, jokes, or casual banter.
- Do not add extra tips, questions, or unrelated guidance for abuse/clarify actions.
- {lang_rule}
""".strip()

    user_prompt = f"""
Conversation history:
{history_text}

Current user message:
{message}
""".strip()

    client = Groq(api_key=GROQ_API_KEY)
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
                max_tokens=220,
            )
            payload = _parse_json_payload((completion.choices[0].message.content or "").strip())
            action = str(payload.get("action", "answer")).strip().lower()
            if action not in {"abuse", "clarify", "answer"}:
                action = "answer"
            assistant_reply = str(payload.get("assistant_reply", "")).strip()

            # Guardrail: avoid false positives where gibberish/noise is mislabeled as abuse.
            if action == "abuse" and not _has_explicit_abuse_markers(message):
                action = "clarify"
                assistant_reply = "I could not understand your message. Please repeat clearly."

            return {"action": action, "assistant_reply": assistant_reply}
        except Exception as exc:
            last_error = exc
            continue

    _ = last_error
    return {"action": "answer", "assistant_reply": ""}


def _language_pref(language: str | None) -> str:
    lang = (language or "en").strip().lower()
    if lang in {"hindi", "hi-in", "hi", "hinglish"}:
        return "hinglish"
    return "en"


def _fallback_chat_reply(kind: str, language: str, role: str) -> str:
    pref = _language_pref(language)
    role_text = role.replace("_", " ").strip() if role else "trade"

    if kind == "abuse":
        if pref == "hinglish":
            return (
                "Warning: Kripya abusive language use na karein."
            )
        return "Warning: Please avoid abusive language."

    if kind == "nonsense":
        if pref == "hinglish":
            return "Mujhe aapka message samajh nahi aaya. Kripya clear way mein dubara boliye."
        return "I could not understand your message. Please repeat clearly."

    if pref == "hinglish":
        return (
            f"Main {role_text} role ke queries ke liye professional guidance provide karunga."
        )
    return (
        f"I provide professional guidance for {role_text} queries."
    )


def _safe_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _normalize_language(language: str | None) -> str:
    if not language:
        return "en"
    lang = str(language).strip().lower()
    if lang in {"hindi", "hi-in", "hin"}:
        return "hi"
    if "-" in lang:
        lang = lang.split("-")[0]
    return lang if lang else "en"


def _normalize_resources(value: Any) -> List[Dict[str, str]]:
    if not isinstance(value, list):
        return []

    resources: List[Dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip()
        resource_type = str(item.get("type", "")).strip().lower()
        url = str(item.get("url", "")).strip()
        language = _normalize_language(str(item.get("language", "")).strip() or "en")

        if not title:
            continue
        if resource_type not in {"youtube", "book", "article", "course", "manual"}:
            resource_type = "article"

        resources.append(
            {
                "title": title,
                "type": resource_type,
                "url": url,
                "language": language,
            }
        )

    return resources[:5]


def _filter_resources_by_language(resources: List[Dict[str, str]], language: str) -> List[Dict[str, str]]:
    target = _normalize_language(language)
    if not resources:
        return []

    preferred = [r for r in resources if _normalize_language(r.get("language", "")) == target]
    neutral = [r for r in resources if _normalize_language(r.get("language", "")) in {"en", "any"}]

    if target == "en":
        ranked = preferred + [r for r in resources if r not in preferred]
    else:
        ranked = preferred + neutral + [r for r in resources if r not in preferred and r not in neutral]

    return ranked[:5]


def _build_user_snapshot(user_data: Dict[str, Any]) -> str:
    role = str(user_data.get("role", "general_worker"))
    skills = _safe_list(user_data.get("skills", []))
    experience = str(user_data.get("experience_level", "beginner"))
    resume_text = str(user_data.get("resume_text", "")).strip()

    return (
        f"Role: {role}\n"
        f"Skills: {', '.join(skills) if skills else 'None'}\n"
        f"Experience: {experience}\n"
        f"Resume: {resume_text if resume_text else 'Not provided'}"
    )


def generate_chat_response(
    message: str,
    user_data: Dict[str, Any],
    history: List[Dict[str, str]],
    language: str = "en",
    selected_role: str | None = None,
) -> str:
    """Return concise career guidance for one chat turn."""

    context = _build_user_snapshot(user_data)
    role = str(selected_role or user_data.get("role") or "blue-collar trade")

    decision = _guidance_turn_decision(message=message, history=history, role=role, language=language)
    action = str(decision.get("action", "answer")).strip().lower()
    assistant_reply = str(decision.get("assistant_reply", "")).strip()

    if action == "abuse":
        return assistant_reply or _fallback_chat_reply("abuse", language, role)

    if action == "clarify":
        return assistant_reply or _fallback_chat_reply("nonsense", language, role)

    try:
        return career_chat_query(
            user_message=message,
            user_context=context,
            chat_history=history or [],
            language=language,
            selected_role=role,
        )
    except Exception:
        return _fallback_chat_reply("error", language, role)


def generate_greeting(user_data: Dict[str, Any], language: str = "en") -> str:
    """Return a short welcome message personalized to profile."""

    context = _build_user_snapshot(user_data)
    prompt = (
        "Generate a short welcome message (max 2 sentences), practical and motivating, "
        f"for language preference: {language}."
    )

    try:
        return career_chat_query(
            user_message=prompt,
            user_context=context,
            chat_history=[],
            language=language,
            selected_role=str(user_data.get("role", "blue-collar trade")),
        )
    except Exception:
        return _fallback_chat_reply("error", language, str(user_data.get("role", "blue-collar trade")))


def _extract_json_array(raw_text: str, language: str = "en") -> List[Dict[str, Any]]:
    match = re.search(r"\[.*\]", raw_text or "", re.DOTALL)
    if not match:
        return []

    try:
        payload = json.loads(match.group())
    except Exception:
        return []

    if not isinstance(payload, list):
        return []

    modules: List[Dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        module = str(item.get("module", "")).strip()
        skills_to_learn = _safe_list(item.get("skills_to_learn", []))
        duration = str(item.get("duration", "")).strip()
        practice_task = str(item.get("practice_task", "")).strip()
        resources = _normalize_resources(item.get("resources", []))
        if not module:
            continue
        modules.append(
            {
                "module": module,
                "skills_to_learn": skills_to_learn,
                "duration": duration,
                "practice_task": practice_task,
                "resources": _filter_resources_by_language(resources, language),
            }
        )

    return modules


def generate_training_recommendations(user_data: Dict[str, Any], language: str | None = None) -> Dict[str, List[Dict[str, Any]]]:
    """Return training recommendations in strict JSON-compatible structure."""

    context = _build_user_snapshot(user_data)
    target_language = _normalize_language(language or str(user_data.get("language", "en")))
    question = (
        "Create training modules for the worker profile. Return ONLY valid JSON array with objects: "
        "module, skills_to_learn (array), duration, practice_task, resources (array of objects with title, type, url, language). "
        "Each module must have at least 2 resources: include practical YouTube links, books, manuals, or courses. "
        f"Prioritize resources in language: {target_language}. "
        "Use real public links when possible. Minimum 3 modules. "
        "Keep practical, blue-collar focused.\n\n"
        f"User profile:\n{context}"
    )

    try:
        raw = rag_query(question=question, user_answer="", chat_history=[])
        modules = _extract_json_array(raw, language=target_language)
    except Exception:
        modules = []

    if not modules:
        role = str(user_data.get("role", "general_worker"))
        modules = [
            {
                "module": f"Core {role.title()} Safety",
                "skills_to_learn": ["workplace safety", "tool handling"],
                "duration": "1 week",
                "practice_task": "Complete a daily safety checklist before work.",
                "resources": [
                    {
                        "title": "OSHA Safety Training Videos",
                        "type": "youtube",
                        "url": "https://www.youtube.com/results?search_query=osha+safety+training",
                        "language": "en",
                    },
                    {
                        "title": "OSHA Quick Start Guide",
                        "type": "manual",
                        "url": "https://www.osha.gov/smallbusiness",
                        "language": "en",
                    },
                    {
                        "title": "Electrical Safety Hindi Training",
                        "type": "youtube",
                        "url": "https://www.youtube.com/results?search_query=electrical+safety+training+hindi",
                        "language": "hi",
                    },
                ],
            },
            {
                "module": "Quality and Efficiency",
                "skills_to_learn": ["measurement accuracy", "error prevention"],
                "duration": "2 weeks",
                "practice_task": "Track and reduce one repeated work error each day.",
                "resources": [
                    {
                        "title": "5S Workplace Organization Basics",
                        "type": "youtube",
                        "url": "https://www.youtube.com/results?search_query=5s+workplace+organization+training",
                        "language": "en",
                    },
                    {
                        "title": "Lean Basics for Shop Floor",
                        "type": "article",
                        "url": "https://www.mindtools.com/azrj5a6/lean-production",
                        "language": "en",
                    },
                    {
                        "title": "5S Training Hindi",
                        "type": "youtube",
                        "url": "https://www.youtube.com/results?search_query=5s+training+hindi",
                        "language": "hi",
                    },
                ],
            },
            {
                "module": "Customer Communication",
                "skills_to_learn": ["job explanation", "issue reporting"],
                "duration": "1 week",
                "practice_task": "Explain completed work in simple steps to one customer.",
                "resources": [
                    {
                        "title": "Customer Service Skills Training",
                        "type": "youtube",
                        "url": "https://www.youtube.com/results?search_query=customer+service+skills+training",
                        "language": "en",
                    },
                    {
                        "title": "Communication Skills Handbook",
                        "type": "book",
                        "url": "https://openlibrary.org/search?q=communication+skills",
                        "language": "en",
                    },
                    {
                        "title": "Customer Communication Hindi",
                        "type": "youtube",
                        "url": "https://www.youtube.com/results?search_query=customer+communication+hindi",
                        "language": "hi",
                    },
                ],
            },
        ]

    for module in modules:
        module["resources"] = _filter_resources_by_language(
            _normalize_resources(module.get("resources", [])),
            target_language,
        )

    return {"modules": modules}
