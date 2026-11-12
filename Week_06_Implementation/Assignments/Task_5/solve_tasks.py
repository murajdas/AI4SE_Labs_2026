from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

TASK3_DIRECTORY = Path(__file__).resolve().parents[1] / "Task_3"
TASK4_DIRECTORY = Path(__file__).resolve().parents[1] / "Task_4"
for directory in (TASK3_DIRECTORY, TASK4_DIRECTORY):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from embedding_repository import embed
from match_embeddings import match

ALLOWED_MODELS = {
    "gpt-6-luna",
    "gpt-5.6-luna",
    "gpt-5.4-nano",
    "gpt-5-nano",
    "gpt-5-mini",
    "gpt-4.1-nano",
    "gpt-4o-mini",
}


def extract_code(response: str) -> str:
    fenced = re.search(r"```(?:python)?\s*(.*?)```", response, re.DOTALL | re.IGNORECASE)
    return (fenced.group(1) if fenced else response).strip()


def call_llm(prompt: str, model: str, endpoint: str, api_key: str) -> str:
    if model not in ALLOWED_MODELS:
        raise ValueError(f"model must be one of: {', '.join(sorted(ALLOWED_MODELS))}")
    request_data = json.dumps(
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only one complete Python method definition. "
                        "Do not include markdown or explanations."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=request_data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM request failed ({error.code}): {details}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"LLM request failed: {error.reason}") from error

    try:
        return payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("LLM response did not contain message content") from error


def replace_method(source: str, class_name: str, method_name: str, returned_code: str) -> str:
    tree = ast.parse(source)
    target: ast.FunctionDef | ast.AsyncFunctionDef | None = None
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == method_name
            and any(
                isinstance(parent, ast.ClassDef) and parent.name == class_name
                for parent in ast.walk(tree)
                for child in getattr(parent, "body", [])
                if child is node
            )
        ):
            target = node
            break
    if target is None:
        raise ValueError(f"could not find {class_name}.{method_name}")

    candidate = extract_code(returned_code)
    candidate_tree = ast.parse(textwrap.dedent(candidate))
    methods = [
        node
        for node in candidate_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if len(methods) != 1 or methods[0].name != method_name:
        raise ValueError(f"LLM must return exactly the {method_name} method definition")

    replacement = textwrap.dedent(candidate).strip("\n")
    indentation = " " * target.col_offset
    replacement = textwrap.indent(replacement, indentation)
    lines = source.splitlines(keepends=True)
    if methods[0].decorator_list:  # the answer brings its own decorators: replace the old ones
        start = min([target.lineno] + [d.lineno for d in target.decorator_list]) - 1
    else:  # the answer has none (e.g. forgot @property): keep the original decorators
        start = target.lineno - 1
    end = target.end_lineno
    newline = "\r\n" if "\r\n" in source else "\n"
    return "".join(lines[:start]) + replacement + newline + "".join(lines[end:])


def describe_task(task: dict[str, Any]) -> str:
    """Return the textual task for one entry of missing_code.json."""
    return (
        f"Implement `{task['class']}.{task['method']}` in `{task['file']}`.\n"
        f"Required behavior and docstring:\n{task['docstring']}"
    )


def retrieve_chunks(task_text: str, store: dict[str, Any], top_k: int = 5) -> list[dict[str, Any]]:
    """Match the ``top_k`` chunks of the storage that are most relevant for the task."""
    query_embedding = embed(task_text, store["idf"], int(store["dimensions"]))
    return match(store, query_embedding, top_k)


def build_prompt(task_text: str, chunks: list[dict[str, Any]]) -> str:
    context = "\n\n".join(
        f"### {item['chunk']['path']}:{item['chunk']['start_line']}-{item['chunk']['end_line']}\n"
        f"{item['chunk']['content']}"
        for item in chunks
    )
    return (
        f"{task_text}\n\n"
        "Use the following repository context. Return only the complete method definition.\n\n"
        f"{context}"
    )


def generate_code(
    task_text: str,
    store: dict[str, Any],
    model: str,
    endpoint: str,
    api_key: str,
    top_k: int = 5,
) -> str:
    """Accept a textual task, match the top chunks, ask the LLM and return its answer."""
    prompt = build_prompt(task_text, retrieve_chunks(task_text, store, top_k))
    return call_llm(prompt, model, endpoint, api_key)


def solve_task(
    task: dict[str, Any],
    store: dict[str, Any],
    repository: Path,
    model: str,
    endpoint: str,
    api_key: str,
) -> Path:
    """Generate the missing method for one task and write it into the target file."""
    returned_code = generate_code(describe_task(task), store, model, endpoint, api_key)
    path = repository / task["file"]
    source = path.read_text(encoding="utf-8")
    # the file is written only after the answer was validated by replace_method
    path.write_text(
        replace_method(source, task["class"], task["method"], returned_code),
        encoding="utf-8",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Solve missing methods through a RAG/LLM pipeline")
    parser.add_argument("tasks", type=Path, help="missing_code.json")
    parser.add_argument("storage", type=Path, help="Task 3 embeddings.json")
    parser.add_argument("repository", type=Path, help="cloned repository root")
    parser.add_argument("--model", default=os.environ.get("RAG_MODEL", "gpt-5-mini"))
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions"),
    )
    parser.add_argument("--dry-run", action="store_true", help="build prompts without writing files")
    args = parser.parse_args()

    if args.model not in ALLOWED_MODELS:
        raise ValueError(f"model must be one of: {', '.join(sorted(ALLOWED_MODELS))}")
    store = json.loads(args.storage.read_text(encoding="utf-8"))
    tasks = json.loads(args.tasks.read_text(encoding="utf-8"))
    api_key = os.environ.get("OPENAI_API_KEY")
    if not args.dry_run and not api_key:
        raise RuntimeError("OPENAI_API_KEY is required unless --dry-run is used")

    failures = []
    for task in tasks:
        name = f"{task['file']}::{task['class']}.{task['method']}"
        if args.dry_run:
            task_text = describe_task(task)
            chunks = retrieve_chunks(task_text, store)
            build_prompt(task_text, chunks)
            print(f"Prepared {name}")
            for item in chunks:
                chunk = item["chunk"]
                print(f"    {item['score']:.4f} {chunk['path']}:{chunk['start_line']}-{chunk['end_line']}")
            continue
        try:
            path = solve_task(task, store, args.repository, args.model, args.endpoint, api_key)
        except (ValueError, RuntimeError, SyntaxError) as error:
            failures.append(name)
            print(f"FAILED {name}: {error}")
            continue
        print(f"Updated {path}::{task['class']}.{task['method']}")

    if failures:
        print(f"{len(failures)} of {len(tasks)} tasks failed: {', '.join(failures)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
