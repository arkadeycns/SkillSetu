"""AI-first RAG feedback with minimal prompting."""

from __future__ import annotations

import os
import re

from groq import Groq

from src.config import GROQ_API_KEY
from src.rag.retriever import retrieve_sops


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


def career_chat_query(user_message: str, user_context: str, chat_history=None) -> str:
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

    system_prompt = f"""
You are a blue-collar career assistant.
Rules:
- Reply naturally in 2-5 short sentences.
- Give practical, task-focused advice.
- Never act like an interview evaluator.
- Never invent that the user answered a specific trade question unless explicitly present.
- If message is only mic test/noise, acknowledge and ask a clear follow-up question.
- If user is abusive, set a firm respectful boundary and continue only if respectful language is used.

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

    reply = _chat_with_fallback(Groq(api_key=GROQ_API_KEY), system_prompt, user_prompt)
    reply = re.sub(r"\s+", " ", (reply or "")).strip()
    if reply:
        return reply

    raise RuntimeError("Groq returned empty career chat response.")
