"""Reusable AI helpers for chat and training recommendations."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from src.rag.qa import career_chat_query, rag_query


ABUSE_PATTERNS = [
    r"\b(?:fuck|f\*+k|bc|mc|chutiya|madarchod|bhosdike|gaand|randi|harami|bastard|idiot|stupid)\b",
]


def _is_abusive(text: str) -> bool:
    lowered = (text or "").lower()
    return any(re.search(pattern, lowered) for pattern in ABUSE_PATTERNS)


def _is_mic_test_or_nonsense(text: str) -> bool:
    msg = (text or "").strip().lower()
    if not msg:
        return True

    if re.search(r"\b(mic|microphone|audio|sound)\b", msg) and re.search(r"\b(test|testing|check|1\s*,?\s*2\s*,?\s*3)\b", msg):
        return True

    alpha_words = re.findall(r"[a-z]+", msg)
    if len(alpha_words) <= 2 and re.search(r"\b(test|hello|check|ok|hmm|hmmm|123)\b", msg):
        return True

    punct = re.sub(r"[\w\s]", "", msg)
    if len(msg) > 0 and len(punct) / max(1, len(msg)) > 0.4:
        return True

    return False


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
                "Please gaali mat do. Main aapki job guidance, training aur interview prep mein madad karunga, "
                "bas respectful language use karein."
            )
        return (
            "Please avoid abusive language. I can help with job guidance, training, and interview preparation "
            "once we keep the conversation respectful."
        )

    if kind == "nonsense":
        if pref == "hinglish":
            return (
                f"Mic check mil gaya, audio theek lag raha hai. Ab {role_text} ka practical sawaal poochiye, "
                "jaise tools, safety ya next skill steps."
            )
        return (
            f"Mic check received. Audio seems fine. Please ask a practical {role_text} question, "
            "for example tools, safety checks, or next training steps."
        )

    if pref == "hinglish":
        return (
            f"Main aapko {role_text} role ke liye step-by-step guidance de sakta hoon. "
            "Ek practical problem bataiye jise aap abhi improve karna chahte hain."
        )
    return (
        f"I can guide you step by step for the {role_text} role. "
        "Tell me one practical problem you want to improve right now."
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

    if _is_abusive(message):
        return _fallback_chat_reply("abuse", language, role)

    if _is_mic_test_or_nonsense(message):
        return _fallback_chat_reply("nonsense", language, role)

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
