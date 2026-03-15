import sys
import os
from pathlib import Path
from groq import Groq

AI_SERVICE_PATH = Path(__file__).resolve().parents[2] / "AI_Service"
sys.path.append(str(AI_SERVICE_PATH))

from src.rag.retriever import retrieve_sops

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {question}\nWorker Answer: {user_answer}"}
            ],
            temperature=0.2,
            max_tokens=120
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"RAG Error: {e}")
        return "Sorry, I cannot access the assessment guidelines right now."