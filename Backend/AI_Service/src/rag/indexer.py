"""Ingest SOP text into Pinecone with Google embeddings."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Dict, Iterable, List
from uuid import uuid4

from google import genai
from pinecone import Pinecone, ServerlessSpec

from AI_Service.src.config import GEMINI_API_KEY, PINECONE_API_KEY

INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "skillsetu-sops-3072")
EMBED_MODEL = "gemini-embedding-001"
PINECONE_CLOUD = os.environ.get("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.environ.get("PINECONE_REGION", "us-east-1")


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


def _ensure_index(pinecone: Pinecone, dimension: int) -> None:
    try:
        description = pinecone.describe_index(INDEX_NAME)
        existing_dimension = int(getattr(description, "dimension", description["dimension"]))
        if existing_dimension != dimension:
            raise ValueError(
                f"Index '{INDEX_NAME}' has dimension {existing_dimension}, but embedding model uses {dimension}. "
                "Use a different PINECONE_INDEX_NAME or recreate the index with matching dimension."
            )
        return
    except Exception as exc:
        # If describe_index fails because index doesn't exist, create it.
        message = str(exc).lower()
        if "not found" not in message and "does not exist" not in message and "404" not in message:
            raise

    pinecone.create_index(
        name=INDEX_NAME,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
    )


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

    sample_embedding = _embed_text(genai_client, chunks[0])
    _ensure_index(pinecone, dimension=len(sample_embedding))
    index = pinecone.Index(INDEX_NAME)

    total_upserted = 0
    for group in _batch(chunks, batch_size):
        vectors = []
        for idx, chunk in enumerate(group):
            embedding = sample_embedding if total_upserted == 0 and idx == 0 else _embed_text(genai_client, chunk)
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
