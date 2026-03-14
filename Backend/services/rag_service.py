import sys
from pathlib import Path

# Allow importing from AI_Service
AI_SERVICE_PATH = Path(__file__).resolve().parents[2] / "AI_Service"
sys.path.append(str(AI_SERVICE_PATH))

from src.rag.retriever import retrieve_sops


def rag_query(question: str):
    """
    Retrieve SOP context using RAG
    """

    try:
        # retrieve context from vector DB
        context_chunks = retrieve_sops(question, top_k=4)

        if not context_chunks:
            return "No relevant SOP information found."

        # merge chunks
        context = "\n\n".join(context_chunks)

        answer = f"""
Based on the SOP knowledge base:

{context}

User Question:
{question}
"""

        return answer.strip()

    except Exception as e:
        return f"RAG pipeline failed: {str(e)}"
