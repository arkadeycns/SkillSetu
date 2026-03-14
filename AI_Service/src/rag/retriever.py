"""Retrieve relevant SOP chunks for a query from Pinecone."""

from __future__ import annotations

from typing import List

from google import genai
from pinecone import Pinecone

from src.config import GEMINI_API_KEY, PINECONE_API_KEY

INDEX_NAME = "skillsetu-sops"
EMBED_MODEL = "text-embedding-004"


def _embed_query(client: genai.Client, text: str) -> List[float]:
    response = client.models.embed_content(model=EMBED_MODEL, contents=text)
    if not response.embeddings:
        raise ValueError("Embedding API returned no vectors for query.")
    return list(response.embeddings[0].values)


def retrieve_sops(query_text: str, top_k: int = 3) -> str:
    """Return concatenated SOP context relevant to the provided query."""
    if not query_text or not query_text.strip():
        return ""
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY in environment.")
    if not PINECONE_API_KEY:
        raise ValueError("Missing PINECONE_API_KEY in environment.")

    genai_client = genai.Client(api_key=GEMINI_API_KEY)
    query_embedding = _embed_query(genai_client, query_text.strip())

    pinecone = Pinecone(api_key=PINECONE_API_KEY)
    index = pinecone.Index(INDEX_NAME)

    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    matches = getattr(results, "matches", []) or []

    sop_chunks = []
    for match in matches:
        metadata = getattr(match, "metadata", None) or {}
        chunk = metadata.get("text")
        if chunk:
            sop_chunks.append(chunk)

    return "\n\n".join(sop_chunks)
