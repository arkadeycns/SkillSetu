"""AI-first RAG feedback with minimal prompting."""

from __future__ import annotations

import os
import re

from groq import Groq

from AI_Service.src.config import GROQ_API_KEY
from AI_Service.src.rag.retriever import retrieve_sops


MODEL_CANDIDATES = [
    os.environ.get("GROQ_CHAT_MODEL", "llama-3.1-8b-instant").strip(),
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]


def _chat_with_fallback(client: Groq, system_prompt: str, user_prompt: str) -> str:
    last_error = None

    for model_name in MODEL_CANDIDATES:
        if not model_name:
            continue

        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=180,
            )
            text = (completion.choices[0].message.content or "").strip()
            if text:
                return text
        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error

    raise ValueError("No chat model configured for RAG responses.")


def _contains_devanagari(text: str) -> bool:
    return bool(re.search(r"[\u0900-\u097F]", text or ""))


def _to_romanized_hindi(client: Groq, text: str) -> str:
    prompt = (
        "Rewrite the following text in natural Hinglish using ONLY Latin characters. "
        "Do not use Devanagari script. Keep meaning same and concise.\n\n"
        f"Text: {text}"
    )
    return _chat_with_fallback(
        client,
        "You convert Hindi text to Romanized Hinglish only.",
        prompt,
    )


def rag_query(question: str, user_answer: str, chat_history=None) -> str:
    """Return concise coaching feedback for one answer."""

    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY for QA feedback generation.")

    try:
        context_chunks = retrieve_sops(question, top_k=4)
        sop_context = "\n\n".join(context_chunks) if context_chunks else "General safety SOP applies."
    except Exception:
        # Retrieval depends on Gemini embeddings; continue with a safe generic context.
        sop_context = "General safety SOP applies."

    history_text = ""
    for item in (chat_history or []):
        history_text += f"Q: {item.get('question', '')}\nA: {item.get('answer_en', '')}\n"

    system_prompt = f"""
You are a practical vocational interview coach.
Use simple language and address the learner as "you".
Give 1-2 short sentences of feedback.
Mention one concrete strength only if present, and one improvement step.
Do not ask a new question.

SOP context:
{sop_context}
""".strip()

    user_prompt = f"""
Conversation history:
{history_text}

Current question:
{question}

Learner answer:
{user_answer}
""".strip()

    reply = _chat_with_fallback(Groq(api_key=GROQ_API_KEY), system_prompt, user_prompt)
    if reply:
        return reply

    raise RuntimeError("Groq returned empty QA feedback.")


def career_chat_query(
    user_message: str,
    user_context: str,
    chat_history=None,
    language: str = "en",
    selected_role: str | None = None,
) -> str:
    """Return practical chat guidance without interview-evaluation behavior."""

    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY for career chat generation.")

    try:
        context_chunks = retrieve_sops(user_message, top_k=3)
        sop_context = "\n\n".join(context_chunks) if context_chunks else "General workplace safety SOP applies."
    except Exception:
        sop_context = "General workplace safety SOP applies."

    history_text = ""
    for item in (chat_history or []):
        history_text += f"User: {item.get('question', '')}\nAssistant: {item.get('answer_en', '')}\n"

    role_hint = (selected_role or "").strip() or "blue-collar trade"
    lang = (language or "en").strip().lower()
    language_rule = "Reply in English."
    if lang in {"hi", "hindi", "hinglish", "hi-in"}:
        language_rule = "Reply in natural Hinglish using ONLY Latin script (Roman Hindi). Never use Devanagari."

    system_prompt = f"""
You are a blue-collar career assistant.
Rules:
- Reply in a professional, respectful tone in 2-5 short sentences.
- Give practical, task-focused advice.
- Never act like an interview evaluator.
- Never invent that the user answered a specific trade question unless explicitly present.
- If message is only mic test/noise, acknowledge and ask a clear follow-up question.
- If user is abusive, set a firm respectful boundary and continue only if respectful language is used.
- Keep guidance specific to user's selected role/trade: {role_hint}.
- Strict role lock: if the user asks for guidance for a different profession than {role_hint}, do not provide that other profession guidance. Instead, politely say you are currently focused on {role_hint} and offer help within {role_hint}. Only switch if user explicitly asks to change role.
- Mention at least one relevant trade step/tool/check where applicable.
- Avoid generic motivational lines unless user explicitly asks.
- Do not use slang, jokes, casual banter, or emojis.
- {language_rule}

SOP context:
{sop_context}
""".strip()

    user_prompt = f"""
User profile:
{user_context}

Conversation history:
{history_text}

Current user message:
{user_message}
""".strip()

    client = Groq(api_key=GROQ_API_KEY)
    reply = _chat_with_fallback(client, system_prompt, user_prompt)
    reply = re.sub(r"\s+", " ", (reply or "")).strip()

    if lang in {"hi", "hindi", "hinglish", "hi-in"} and _contains_devanagari(reply):
        reply = re.sub(r"\s+", " ", _to_romanized_hindi(client, reply)).strip()

    if reply:
        return reply

    raise RuntimeError("Groq returned empty career chat response.")
