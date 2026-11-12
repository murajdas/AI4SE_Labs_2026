from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import List, Tuple

DEFAULT_EXCLUDED_DIRECTORIES = {".git", "__pycache__", ".pytest_cache"}
DEFAULT_EXCLUDED_FILES = {".gitignore"}
Unit = Tuple[int, int, List[str], bool]


def is_text_file(path: Path) -> bool:
    try:
        data = path.read_bytes()
        data.decode("utf-8")
    except OSError:
        return False
    except UnicodeDecodeError:
        return False
    return b"\x00" not in data


def size(lines: list[str], start: int, end: int) -> int:
    return sum(len(line) for line in lines[start - 1 : end])


def line_windows(
    lines: list[str], start: int, end: int, max_chars: int, overlap: int
) -> list[tuple[int, int]]:

    windows = []
    first = start
    while first <= end:
        last, total = first, 0
        while last <= end and (last == first or total + len(lines[last - 1]) <= max_chars):
            total += len(lines[last - 1])
            last += 1
        last -= 1
        windows.append((first, last))
        if last >= end:
            break
        first = max(last - overlap + 1, first + 1)  # always make progress
    return windows


def python_units(
    nodes: list[ast.stmt],
    lines: list[str],
    region_start: int,
    region_end: int,
    scope: str | None,
    max_chars: int,
    overlap: int,
) -> list[Unit]:
    starts: list[int] = []
    previous_end = region_start - 1
    for node in nodes:
        start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        while start - 1 > previous_end and lines[start - 2].lstrip().startswith("#"):
            start -= 1
        starts.append(start)
        previous_end = node.end_lineno

    units: list[Unit] = []
    first = starts[0] if starts else region_end + 1
    if first > region_start:  # module header, or the "class X:" line
        units.append((region_start, first - 1, [scope] if scope else [], True))

    for index, node in enumerate(nodes):
        start = starts[index]
        end = starts[index + 1] - 1 if index + 1 < len(nodes) else region_end
        name = getattr(node, "name", None)
        qualified = f"{scope}.{name}" if scope and name else name
        symbols = [qualified] if qualified else []
        if isinstance(node, ast.ClassDef):
            symbols += [
                f"{qualified}.{member.name}"
                for member in node.body
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]

        if size(lines, start, end) <= max_chars:
            units.append((start, end, symbols, True))
        elif isinstance(node, ast.ClassDef):  # class too big: header + its members
            units.extend(
                python_units(node.body, lines, start, end, qualified, max_chars, overlap)
            )
        else:  # a function (or other statement) bigger than the limit
            for window_start, window_end in line_windows(lines, start, end, max_chars, overlap):
                units.append((window_start, window_end, symbols, False))
    return units


def merge_units(units: list[Unit], lines: list[str], max_chars: int, min_chars: int) -> list[Unit]:
    merged: list[Unit] = []
    for start, end, symbols, mergeable in units:
        if merged:
            prev_start, _, prev_symbols, prev_mergeable = merged[-1]
            if (
                prev_mergeable
                and mergeable
                and size(lines, prev_start, merged[-1][1]) < min_chars
                and size(lines, prev_start, end) <= max_chars
            ):
                merged[-1] = (prev_start, end, prev_symbols + symbols, True)
                continue
        merged.append((start, end, symbols, mergeable))
    return merged


def chunk_file(
    path: Path, repository_root: Path, max_chars: int, min_chars: int, overlap: int
) -> list[dict]:
    """Create chunks for one text file."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    units: list[Unit] = []

    if path.suffix == ".py" and lines:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        if tree is not None:
            units = python_units(tree.body, lines, 1, len(lines), None, max_chars, overlap)
            units = merge_units(units, lines, max_chars, min_chars)
    if not units and lines:  # not Python (or not parsable): plain line windows
        units = [
            (start, end, [], False)
            for start, end in line_windows(lines, 1, len(lines), max_chars, overlap)
        ]

    chunks = []
    for start, end, symbols, _ in units:
        while start < end and not lines[start - 1].strip():  # trim blank edges
            start += 1
        while end > start and not lines[end - 1].strip():
            end -= 1
        content = "".join(lines[start - 1 : end]).rstrip()
        if not content:
            continue
        chunks.append(
            {
                "path": path.relative_to(repository_root).as_posix(),
                "start_line": start,
                "end_line": end,
                "symbols": list(dict.fromkeys(symbols)),
                "content": content,
            }
        )
    return chunks


def build_chunks(
    repository_root: Path,
    max_chars: int = 1500,
    min_chars: int = 600,
    overlap: int = 3,
) -> list[dict]:
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than zero")
    if min_chars < 0 or min_chars > max_chars:
        raise ValueError("min_chars must be non-negative and not greater than max_chars")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")

    chunks = []
    for path in sorted(repository_root.rglob("*")):
        relative_parts = path.relative_to(repository_root).parts
        if (
            not path.is_file()
            or any(part in DEFAULT_EXCLUDED_DIRECTORIES for part in relative_parts)
            or path.name in DEFAULT_EXCLUDED_FILES
            or not is_text_file(path)
        ):
            continue
        chunks.extend(chunk_file(path, repository_root, max_chars, min_chars, overlap))
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path, help="repository to chunk")
    parser.add_argument("output", type=Path, help="JSON file receiving the chunks")
    parser.add_argument("--max-chars", type=int, default=1500, help="maximum chunk size")
    parser.add_argument("--min-chars", type=int, default=600, help="merge chunks smaller than this")
    parser.add_argument("--overlap", type=int, default=3, help="overlap in lines when a unit is cut")
    args = parser.parse_args()

    repository_root = args.repository.resolve()
    chunks = build_chunks(repository_root, args.max_chars, args.min_chars, args.overlap)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "max_chars": args.max_chars,
                "min_chars": args.min_chars,
                "overlap": args.overlap,
                "chunks": chunks,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(chunks)} chunks to {args.output}")


if __name__ == "__main__":
    main()
