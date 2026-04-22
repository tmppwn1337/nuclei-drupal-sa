#!/usr/bin/env python3
"""Extract path-like strings from repository files and write them to extracted-paths.txt."""

from __future__ import annotations

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = REPO_ROOT / "extracted-paths.txt"
EXCLUDED_FILES = {OUTPUT_FILE.name}
EXCLUDED_DIRS = {".git"}

PATH_PATTERNS = [
    re.compile(r"\b(?:https?|file)://[^\s\"'<>]+"),
    re.compile(r"(?<![\w.-])/(?:[A-Za-z0-9._~!$&+,;=:@%\-]+/?)+"),
    re.compile(r"(?<![\w.-])\.\./(?:[A-Za-z0-9._~!$&+,;=:@%\-]+/?)+"),
    re.compile(r"(?<![\w.-])\./(?:[A-Za-z0-9._~!$&+,;=:@%\-]+/?)+"),
    re.compile(r"(?<![\w.-])(?:[a-z0-9._\-]+/){1,}[a-z0-9._\-]+/?"),
]


def iter_repo_files(root: Path):
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in files:
            if name in EXCLUDED_FILES:
                continue
            yield Path(current_root) / name


def normalize_match(value: str) -> str:
    return value.strip().strip("\"'`.,;:!?)]}").lstrip("([{\"'`")


def extract_paths(content: str) -> set[str]:
    matches = set()
    for pattern in PATH_PATTERNS:
        for match in pattern.findall(content):
            cleaned = normalize_match(match)
            if "/" in cleaned:
                matches.add(cleaned)
    return matches


def main() -> None:
    collected = set()

    for file_path in iter_repo_files(REPO_ROOT):
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        collected.update(extract_paths(content))

    OUTPUT_FILE.write_text("\n".join(sorted(collected)) + "\n", encoding="utf-8")
    print(f"Extracted {len(collected)} unique path-like values to {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
