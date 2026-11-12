"""Build chunk embeddings (hashed TF-IDF vectors) and search them by cosine similarity."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

IDENTIFIER_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+")
CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def tokens(text: str) -> list[str]:
    """Split text into lowercase tokens.

    An identifier such as ``BulkDiscountPricing`` or ``add_item`` yields the
    whole identifier and its words (``bulk``, ``discount``, ``pricing``).
    """
    result = []
    for match in IDENTIFIER_PATTERN.finditer(text):
        identifier = match.group(0)
        words = [
            word.lower()
            for part in identifier.split("_")
            for word in CAMEL_BOUNDARY.split(part)
            if word
        ]
        if len(words) > 1:
            result.append(identifier.lower())
        result.extend(words)
    return result


def chunk_text(chunk: dict[str, Any]) -> str:
    """Return the representation of a chunk that is embedded: path, symbols and code."""
    return "\n".join([chunk["path"], " ".join(chunk.get("symbols", [])), chunk["content"]])


def compute_idf(documents: list[list[str]]) -> dict[str, float]:
    """Return a smoothed inverse document frequency for every token."""
    frequency = Counter(token for document in documents for token in set(document))
    return {
        token: round(math.log((1 + len(documents)) / (1 + count)) + 1, 6)
        for token, count in sorted(frequency.items())
    }


def embed_tokens(token_list: list[str], idf: dict[str, float], dimensions: int) -> list[float]:
    """Hash weighted tokens into a unit-length vector (signed hashing trick)."""
    if dimensions <= 0:
        raise ValueError("dimensions must be greater than zero")

    vector = [0.0] * dimensions
    for token, count in Counter(token_list).items():
        if token not in idf:  # unknown token cannot match any chunk
            continue
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:8], "big") % dimensions
        sign = 1.0 if digest[8] % 2 == 0 else -1.0
        vector[index] += sign * (1.0 + math.log(count)) * idf[token]

    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]
    return vector


def embed(text: str, idf: dict[str, float], dimensions: int) -> list[float]:
    return embed_tokens(tokens(text), idf, dimensions)


def build_store(chunks_data: dict[str, Any], dimensions: int) -> dict[str, Any]:
    chunks = chunks_data.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError("input JSON must contain a 'chunks' list")
    for chunk in chunks:
        if not isinstance(chunk, dict) or not isinstance(chunk.get("content"), str):
            raise ValueError("every chunk must be an object with string content")
        if not isinstance(chunk.get("path"), str):
            raise ValueError("every chunk must have a string path")

    documents = [tokens(chunk_text(chunk)) for chunk in chunks]
    idf = compute_idf(documents)
    items = [
        {
            "chunk": chunk,
            "embedding": [round(v, 6) for v in embed_tokens(document, idf, dimensions)],
        }
        for chunk, document in zip(chunks, documents)
    ]
    return {
        "method": "hashed TF-IDF (signed hashing trick) with cosine similarity",
        "embedded_text": "path + symbols + content",
        "dimensions": dimensions,
        "idf": idf,
        "items": items,
    }


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vectors must have the same dimensions")
    return sum(a * b for a, b in zip(left, right))


def search(store: dict[str, Any], query: str, top_k: int) -> list[dict[str, Any]]:
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    query_vector = embed(query, store["idf"], int(store["dimensions"]))
    scored = [
        {"score": cosine_similarity(query_vector, item["embedding"]), "chunk": item["chunk"]}
        for item in store["items"]
    ]
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and query chunk embeddings")
    parser.add_argument("chunks", type=Path, help="chunks.json from Task 2")
    parser.add_argument("output", type=Path, help="embedding storage JSON")
    parser.add_argument("--dimensions", type=int, default=512)
    parser.add_argument("--query", help="retrieve the most similar chunks")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--search-only",
        action="store_true",
        help="do not rebuild: search in the existing storage file",
    )
    args = parser.parse_args()

    if args.search_only:
        store = json.loads(args.output.read_text(encoding="utf-8"))
    else:
        chunks_data = json.loads(args.chunks.read_text(encoding="utf-8"))
        store = build_store(chunks_data, args.dimensions)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(store, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {len(store['items'])} embeddings to {args.output}")

    if args.query:
        for result in search(store, args.query, args.top_k):
            chunk = result["chunk"]
            print(
                f"{result['score']:.4f} {chunk['path']}:{chunk['start_line']}-{chunk['end_line']}"
                f" {', '.join(chunk.get('symbols', [])[:2])}"
            )


if __name__ == "__main__":
    main()
