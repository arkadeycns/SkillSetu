"""Ingest SOP text into Pinecone with Google embeddings."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, List
from uuid import uuid4

from google import genai
from pinecone import Pinecone

from src.config import GEMINI_API_KEY, PINECONE_API_KEY

INDEX_NAME = "skillsetu-sops"
EMBED_MODEL = "text-embedding-004"


def _chunk_text(raw_text: str) -> List[str]:
    """Split SOP content by paragraph and drop empty chunks."""
    chunks: List[str] = []
    for block in raw_text.split("\n\n"):
        cleaned = " ".join(line.strip() for line in block.splitlines() if line.strip())
        if cleaned:
            chunks.append(cleaned)
    return chunks


def _embed_text(client: genai.Client, text: str) -> List[float]:
    response = client.models.embed_content(model=EMBED_MODEL, contents=text)
    if not response.embeddings:
        raise ValueError("Embedding API returned no vectors.")
    return list(response.embeddings[0].values)


def _batch(iterable: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def index_sops_from_file(file_path: str, batch_size: int = 25) -> Dict[str, int]:
    """Read SOP file, embed chunks, and upsert to Pinecone in batches."""
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY in environment.")
    if not PINECONE_API_KEY:
        raise ValueError("Missing PINECONE_API_KEY in environment.")

    source = Path(file_path)
    if not source.exists():
        raise FileNotFoundError(f"SOP file not found: {file_path}")

    raw_text = source.read_text(encoding="utf-8")
    chunks = _chunk_text(raw_text)
    if not chunks:
        raise ValueError("No SOP chunks were created. Check file formatting.")

    genai_client = genai.Client(api_key=GEMINI_API_KEY)
    pinecone = Pinecone(api_key=PINECONE_API_KEY)
    index = pinecone.Index(INDEX_NAME)

    total_upserted = 0
    for group in _batch(chunks, batch_size):
        vectors = []
        for chunk in group:
            embedding = _embed_text(genai_client, chunk)
            vectors.append(
                {
                    "id": str(uuid4()),
                    "values": embedding,
                    "metadata": {"text": chunk, "source": source.name},
                }
            )

        index.upsert(vectors=vectors)
        total_upserted += len(vectors)

    return {"chunks": len(chunks), "upserted": total_upserted}


def main() -> None:
    parser = argparse.ArgumentParser(description="Index SOP text file into Pinecone.")
    parser.add_argument("file_path", help="Path to raw SOP text file.")
    parser.add_argument("--batch-size", type=int, default=25)
    args = parser.parse_args()

    result = index_sops_from_file(args.file_path, batch_size=args.batch_size)
    print(f"Indexed {result['upserted']} chunks from {args.file_path}")


if __name__ == "__main__":
    main()
