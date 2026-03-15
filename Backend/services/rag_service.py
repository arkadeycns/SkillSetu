import sys
import os
from pathlib import Path
from groq import Groq

AI_SERVICE_PATH = Path(__file__).resolve().parents[2] / "AI_Service"
sys.path.append(str(AI_SERVICE_PATH))

from src.rag.retriever import retrieve_sops

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL_CANDIDATES = [
    os.environ.get("GROQ_CHAT_MODEL", "").strip(),
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]


def _chat_with_fallback(system_prompt: str, question: str, user_answer: str) -> str:
    last_error = None
    for model_name in MODEL_CANDIDATES:
        if not model_name:
            continue
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {question}\nWorker Answer: {user_answer}"}
                ],
                temperature=0.2,
                max_tokens=120
            )
            return completion.choices[0].message.content.strip()
        except Exception as exc:
            last_error = exc
            print(f"RAG model '{model_name}' failed: {exc}")

    if last_error:
        raise last_error
    raise ValueError("No chat model configured for RAG responses.")

def rag_query(question: str, user_answer: str):
    try:
        # retrieve SOPs using the QUESTION (better semantic match)
        context_chunks = retrieve_sops(question, top_k=4)

        if not context_chunks:
            context = "General safety guidelines apply."
        else:
            context = "\n\n".join(context_chunks)

        system_prompt = f"""
You are an expert AI vocational examiner assessing blue-collar workers.

OFFICIAL SOPs:
{context}

RULES:
- Respond in 2-3 conversational sentences.
- First appreciate what the worker got right.
- Then gently correct missing safety steps.
- Do NOT quote SOPs directly.
"""
        return _chat_with_fallback(system_prompt, question, user_answer)

    except Exception as e:
        print(f"RAG Error: {e}")
        return "Sorry, I cannot access the assessment guidelines right now."