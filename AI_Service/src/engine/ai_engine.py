"""Reusable AI helpers for chat and training recommendations."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

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

TRAINING_PRIORITIES = {"high": 0, "medium": 1, "low": 2}


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


def _safe_text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def _normalize_priority(value: Any) -> str:
    p = _safe_text(value, "medium").lower()
    if p in TRAINING_PRIORITIES:
        return p
    return "medium"


def _normalize_module_name(name: str) -> str:
    text = _safe_text(name).lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _coerce_positive_int(value: Any, default: int = 8) -> int:
    try:
        out = int(float(str(value).strip()))
        return out if out > 0 else default
    except Exception:
        return default


def _is_valid_public_url(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def _is_search_result_url(url: str) -> bool:
    lowered = _safe_text(url).lower()
    return "youtube.com/results?search_query=" in lowered or "google.com/search" in lowered


def _resource_quality_score(resource: Dict[str, str], target_language: str) -> int:
    score = 0
    lang = _normalize_language(resource.get("language", "en"))
    r_type = _safe_text(resource.get("type", "article")).lower()
    url = _safe_text(resource.get("url", ""))

    if lang == target_language:
        score += 4
    elif lang in {"en", "any"}:
        score += 2

    if _is_valid_public_url(url):
        score += 3
    if url and not _is_search_result_url(url):
        score += 2

    if r_type in {"manual", "course", "youtube", "book"}:
        score += 1

    return score


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
        if url and not _is_valid_public_url(url):
            continue

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

    deduped: List[Dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for resource in resources:
        key = (_safe_text(resource.get("title", "")).lower(), _safe_text(resource.get("url", "")).lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(resource)

    ranked = sorted(
        deduped,
        key=lambda r: _resource_quality_score(r, target),
        reverse=True,
    )
    return ranked[:5]


def _build_user_snapshot(user_data: Dict[str, Any]) -> str:
    role = str(user_data.get("role", "general_worker"))
    skills = _safe_list(user_data.get("skills", []))
    experience = str(user_data.get("experience_level", "beginner"))
    resume_text = str(user_data.get("resume_text", "")).strip()
    strengths = _safe_list(user_data.get("strengths", []))
    gaps = _safe_list(user_data.get("gaps", []))

    return (
        f"Role: {role}\n"
        f"Skills: {', '.join(skills) if skills else 'None'}\n"
        f"Strengths: {', '.join(strengths) if strengths else 'None'}\n"
        f"Skill gaps: {', '.join(gaps) if gaps else 'None'}\n"
        f"Experience: {experience}\n"
        f"Resume: {resume_text if resume_text else 'Not provided'}"
    )


def _build_training_user_snapshot(user_data: Dict[str, Any], target_language: str) -> str:
    role = _safe_text(user_data.get("role"), "general_worker")
    skills = _safe_list(user_data.get("skills", []))
    strengths = _safe_list(user_data.get("strengths", []))
    gaps = _safe_list(user_data.get("gaps", []))
    experience = _safe_text(user_data.get("experience_level"), "beginner")
    resume_text = _safe_text(user_data.get("resume_text", ""), "Not provided")

    if experience == "assessed_candidate":
        inferred = "intermediate" if len(gaps) <= 2 else "beginner"
    else:
        inferred = experience

    return (
        f"Role: {role}\n"
        f"Target language: {target_language}\n"
        f"Current skills: {', '.join(skills) if skills else 'None'}\n"
        f"Verified strengths: {', '.join(strengths) if strengths else 'None'}\n"
        f"Verified gaps to fix first: {', '.join(gaps) if gaps else 'None'}\n"
        f"Experience level: {experience}\n"
        f"Inferred proficiency: {inferred}\n"
        f"Resume context: {resume_text}"
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
        module = _safe_text(item.get("module", ""))
        skills_to_learn = _safe_list(item.get("skills_to_learn", []))
        duration = _safe_text(item.get("duration", ""), "1 week")
        practice_task = _safe_text(item.get("practice_task", ""), "Practice one real-world task daily.")
        priority = _normalize_priority(item.get("priority", "medium"))
        why_this_module = _safe_text(item.get("why_this_module", ""), "Improves practical job performance.")
        entry_criteria = _safe_text(item.get("entry_criteria", ""), "Basic familiarity with daily work tools.")
        completion_criteria = _safe_text(item.get("completion_criteria", ""), "Can perform tasks safely with minimal supervision.")
        measurable_outcome = _safe_text(item.get("measurable_outcome", ""), "Complete one supervised job without critical errors.")
        estimated_hours = _coerce_positive_int(item.get("estimated_hours", 8), default=8)
        resources = _normalize_resources(item.get("resources", []))
        if not module:
            continue
        modules.append(
            {
                "module": module,
                "skills_to_learn": skills_to_learn,
                "duration": duration,
                "practice_task": practice_task,
                "priority": priority,
                "why_this_module": why_this_module,
                "entry_criteria": entry_criteria,
                "completion_criteria": completion_criteria,
                "measurable_outcome": measurable_outcome,
                "estimated_hours": estimated_hours,
                "resources": _filter_resources_by_language(resources, language),
            }
        )

    return modules


def _build_training_prompt(context: str, target_language: str, strict_retry: bool = False) -> str:
    retry_clause = ""
    if strict_retry:
        retry_clause = (
            "Previous output was low quality. Correct by ensuring modules are role-specific, "
            "prioritized by strongest gap coverage, and contain measurable outcomes."
        )

    return (
        "Create a personalized upskilling roadmap for a blue-collar worker. "
        "Return ONLY a valid JSON array with 3 to 5 objects.\n"
        "Each object must include EXACT keys: "
        "module, priority, why_this_module, skills_to_learn, duration, estimated_hours, "
        "practice_task, entry_criteria, completion_criteria, measurable_outcome, resources.\n"
        "Constraints:\n"
        "- priority must be high|medium|low\n"
        "- skills_to_learn must be array with at least 2 items\n"
        "- resources must contain at least 2 items; each resource object keys: title, type, url, language\n"
        "- type must be one of youtube|book|article|course|manual\n"
        "- prioritize fixing listed skill gaps first before advanced topics\n"
        "- avoid software topics unless profile is explicitly software\n"
        f"- prioritize resources in language: {target_language}\n"
        "- keep actions practical, job-floor focused, and measurable\n"
        f"{retry_clause}\n\n"
        f"Worker profile:\n{context}"
    )


def _fallback_training_modules(role: str, target_language: str, gaps: List[str]) -> List[Dict[str, Any]]:
    role_title = role.replace("_", " ").strip().title() or "Worker"
    gap_focus = gaps[0] if gaps else "safety and execution"
    modules = [
        {
            "module": f"{role_title} Safety Fundamentals",
            "priority": "high",
            "why_this_module": f"Directly improves {gap_focus} with safe work habits.",
            "skills_to_learn": ["workplace safety", "PPE compliance", "hazard spotting"],
            "duration": "1 week",
            "estimated_hours": 8,
            "practice_task": "Run a pre-task safety checklist before each shift.",
            "entry_criteria": "Beginner friendly.",
            "completion_criteria": "Executes checklist correctly for 5 consecutive shifts.",
            "measurable_outcome": "Zero safety violations across one week.",
            "resources": [
                {
                    "title": "OSHA Small Business Safety Guide",
                    "type": "manual",
                    "url": "https://www.osha.gov/smallbusiness",
                    "language": "en",
                },
                {
                    "title": "Basic Workplace Safety Training",
                    "type": "youtube",
                    "url": "https://www.youtube.com/results?search_query=basic+workplace+safety+training",
                    "language": "en",
                },
            ],
        },
        {
            "module": "Quality and Error Prevention",
            "priority": "high" if gaps else "medium",
            "why_this_module": "Reduces rework and builds reliable execution.",
            "skills_to_learn": ["inspection basics", "measurement accuracy", "error prevention"],
            "duration": "2 weeks",
            "estimated_hours": 12,
            "practice_task": "Log one repeated error daily and prevent it next attempt.",
            "entry_criteria": "Understands daily work sequence.",
            "completion_criteria": "Demonstrates repeatable quality process.",
            "measurable_outcome": "At least 30% reduction in repeat mistakes.",
            "resources": [
                {
                    "title": "5S Workplace Organization Basics",
                    "type": "youtube",
                    "url": "https://www.youtube.com/results?search_query=5s+workplace+organization+training",
                    "language": "en",
                },
                {
                    "title": "Lean Production Basics",
                    "type": "article",
                    "url": "https://www.mindtools.com/azrj5a6/lean-production",
                    "language": "en",
                },
            ],
        },
        {
            "module": "Customer and Team Communication",
            "priority": "low",
            "why_this_module": "Improves clarity, handover, and customer trust.",
            "skills_to_learn": ["job explanation", "issue reporting", "handover clarity"],
            "duration": "1 week",
            "estimated_hours": 6,
            "practice_task": "Explain one completed job daily in clear steps.",
            "entry_criteria": "Can describe basic task steps.",
            "completion_criteria": "Provides clear job updates without missing key details.",
            "measurable_outcome": "Customer/team clarification questions reduced by 25%.",
            "resources": [
                {
                    "title": "Customer Service Skills Training",
                    "type": "youtube",
                    "url": "https://www.youtube.com/results?search_query=customer+service+skills+training",
                    "language": "en",
                },
                {
                    "title": "Communication Skills Open Library",
                    "type": "book",
                    "url": "https://openlibrary.org/search?q=communication+skills",
                    "language": "en",
                },
            ],
        },
    ]

    for module in modules:
        module["resources"] = _filter_resources_by_language(
            _normalize_resources(module.get("resources", [])),
            target_language,
        )
    return modules


def _module_gap_hits(module: Dict[str, Any], gaps: List[str]) -> int:
    if not gaps:
        return 0
    haystack = " ".join(
        [
            _safe_text(module.get("module", "")).lower(),
            _safe_text(module.get("why_this_module", "")).lower(),
            " ".join(_safe_list(module.get("skills_to_learn", []))).lower(),
        ]
    )
    return sum(1 for gap in gaps if gap and gap.lower() in haystack)


def _postprocess_training_modules(
    modules: List[Dict[str, Any]],
    user_data: Dict[str, Any],
    target_language: str,
) -> List[Dict[str, Any]]:
    role = _safe_text(user_data.get("role"), "general_worker")
    gaps = [g.lower() for g in _safe_list(user_data.get("gaps", []))]
    strengths = _safe_list(user_data.get("strengths", []))
    skills = _safe_list(user_data.get("skills", []))

    deduped: List[Dict[str, Any]] = []
    seen_names: set[str] = set()
    for module in modules:
        name = _normalize_module_name(_safe_text(module.get("module", "")))
        if not name or name in seen_names:
            continue
        seen_names.add(name)

        module_skills = _safe_list(module.get("skills_to_learn", []))
        if len(module_skills) < 2:
            seed = [*gaps[:2], *[s for s in strengths if s.lower() not in gaps], *skills]
            module_skills = [s for s in seed if s][:2] or ["safety", "quality"]

        item = {
            "module": _safe_text(module.get("module", "")),
            "priority": _normalize_priority(module.get("priority", "medium")),
            "why_this_module": _safe_text(module.get("why_this_module", ""), f"Builds role readiness for {role} tasks."),
            "skills_to_learn": module_skills,
            "duration": _safe_text(module.get("duration", ""), "1 week"),
            "estimated_hours": _coerce_positive_int(module.get("estimated_hours", 8), default=8),
            "practice_task": _safe_text(module.get("practice_task", ""), "Practice one real task daily with supervisor feedback."),
            "entry_criteria": _safe_text(module.get("entry_criteria", ""), "Basic familiarity with tools and process."),
            "completion_criteria": _safe_text(module.get("completion_criteria", ""), "Can perform tasks with safe and consistent execution."),
            "measurable_outcome": _safe_text(module.get("measurable_outcome", ""), "Improved consistency and fewer errors during supervised work."),
            "resources": _filter_resources_by_language(
                _normalize_resources(module.get("resources", [])),
                target_language,
            ),
        }

        deduped.append(item)

    ranked = sorted(
        deduped,
        key=lambda m: (
            TRAINING_PRIORITIES.get(_normalize_priority(m.get("priority", "medium")), 1),
            -_module_gap_hits(m, gaps),
        ),
    )

    if len(ranked) < 3:
        for fallback in _fallback_training_modules(role, target_language, gaps):
            fallback_name = _normalize_module_name(fallback.get("module", ""))
            if fallback_name in seen_names:
                continue
            seen_names.add(fallback_name)
            ranked.append(fallback)
            if len(ranked) >= 3:
                break

    return ranked[:5]


def _score_training_plan(modules: List[Dict[str, Any]], user_data: Dict[str, Any], target_language: str) -> int:
    if not modules:
        return 0

    gaps = [g.lower() for g in _safe_list(user_data.get("gaps", []))]

    module_count_score = 20 if 3 <= len(modules) <= 5 else 10
    practical_score = 0
    resources_score = 0
    gap_score = 0
    language_score = 0

    for module in modules:
        has_fields = all(
            _safe_text(module.get(key, ""))
            for key in ["why_this_module", "practice_task", "completion_criteria", "measurable_outcome"]
        )
        if has_fields:
            practical_score += 8

        resources = _safe_list(module.get("resources", []))
        if isinstance(module.get("resources"), list) and len(module.get("resources", [])) >= 2:
            resources_score += 6

        if _module_gap_hits(module, gaps) > 0:
            gap_score += 7

        if any(
            _normalize_language(str(r.get("language", ""))) == target_language
            for r in (module.get("resources", []) if isinstance(module.get("resources"), list) else [])
        ):
            language_score += 4

    total = module_count_score + practical_score + resources_score + gap_score + language_score
    return min(100, max(0, total))


def generate_training_recommendations(user_data: Dict[str, Any], language: str | None = None) -> Dict[str, List[Dict[str, Any]]]:
    """Return training recommendations in strict JSON-compatible structure."""

    target_language = _normalize_language(language or str(user_data.get("language", "en")))
    context = _build_training_user_snapshot(user_data, target_language)
    question = _build_training_prompt(context, target_language, strict_retry=False)

    try:
        raw = rag_query(question=question, user_answer="", chat_history=[])
        modules = _postprocess_training_modules(
            _extract_json_array(raw, language=target_language),
            user_data,
            target_language,
        )
    except Exception:
        modules = []

    score = _score_training_plan(modules, user_data, target_language)

    if 0 < len(modules) < 3 or score < 65:
        try:
            retry_prompt = _build_training_prompt(context, target_language, strict_retry=True)
            retry_raw = rag_query(question=retry_prompt, user_answer="", chat_history=[])
            retry_modules = _postprocess_training_modules(
                _extract_json_array(retry_raw, language=target_language),
                user_data,
                target_language,
            )
            retry_score = _score_training_plan(retry_modules, user_data, target_language)
            if retry_score >= score and retry_modules:
                modules = retry_modules
                score = retry_score
        except Exception:
            pass

    if not modules:
        role = _safe_text(user_data.get("role"), "general_worker")
        modules = _fallback_training_modules(role, target_language, _safe_list(user_data.get("gaps", [])))
        score = _score_training_plan(modules, user_data, target_language)

    for module in modules:
        module["resources"] = _filter_resources_by_language(
            _normalize_resources(module.get("resources", [])),
            target_language,
        )

    return {
        "modules": modules,
        "quality_score": score,
        "target_language": target_language,
    }
