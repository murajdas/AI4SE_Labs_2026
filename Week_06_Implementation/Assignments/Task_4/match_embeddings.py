from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TASK3_DIRECTORY = Path(__file__).resolve().parents[1] / "Task_3"
if str(TASK3_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(TASK3_DIRECTORY))


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("input embedding has the wrong number of dimensions")
    return sum(a * b for a, b in zip(left, right))


def match(
    store: dict[str, Any], query_embedding: list[float], top_k: int
) -> list[dict[str, Any]]:
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")
    if len(query_embedding) != store["dimensions"]:
        raise ValueError("input embedding has the wrong number of dimensions")

    results = [
        {
            "score": cosine_similarity(query_embedding, item["embedding"]),
            "chunk": item["chunk"],
        }
        for item in store["items"]
    ]
    return sorted(results, key=lambda result: result["score"], reverse=True)[:top_k]


def load_embedding(path: Path) -> list[float]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(value, dict):
        value = value.get("embedding")
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(component, (int, float)) for component in value)
    ):
        raise ValueError("embedding file must contain a non-empty numeric JSON list")
    return [float(component) for component in value]


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve the most relevant chunks")
    parser.add_argument("storage", type=Path, help="embeddings.json from Task 3")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--query", help="task text to embed and match")
    source.add_argument("--embedding", type=Path, help="JSON file containing an embedding")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    store = json.loads(args.storage.read_text(encoding="utf-8-sig"))
    if args.query is not None:
        from embedding_repository import embed

        query_embedding = embed(args.query, store["idf"], int(store["dimensions"]))
    else:
        query_embedding = load_embedding(args.embedding)

    for result in match(store, query_embedding, args.top_k):
        chunk = result["chunk"]
        print(
            f"{result['score']:.4f} "
            f"{chunk['path']}:{chunk['start_line']}-{chunk['end_line']}"
        )


if __name__ == "__main__":
    main()
