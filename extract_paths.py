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

BASEURL_PATH_PATTERN = re.compile(r"\{\{(?:BaseURL|RootURL)\}\}([^\s\"'<>]+)")
PATH_PATTERNS = [
    re.compile(r"(?<![:/\w.-])/(?:[A-Za-z0-9._~!$&+,;=:@%\-]+/?)+"),
    re.compile(r"(?<![\w.-])\.\./(?:[A-Za-z0-9._~!$&+,;=:@%\-]+/?)+"),
    re.compile(r"(?<![\w.-])\./(?:[A-Za-z0-9._~!$&+,;=:@%\-]+/?)+"),
    re.compile(r"(?<![\w.-])(?:[a-z0-9._\-]+/){1,}[a-z0-9._\-]+/?"),
]
FUZZ_SUBPATH_PREFIXES = (
    "/sites/",
    "/admin/",
    "/postfile/",
    "/core/",
    "/modules/",
    "/misc/",
    "/profiles/",
    "/themes/",
)
FUZZ_EXACT_OR_SUBPATH = ("/node", "/user")


def iter_repo_files(root: Path):
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in files:
            if name in EXCLUDED_FILES:
                continue
            yield Path(current_root) / name


def normalize_match(value: str) -> str:
    return value.strip("\"'`.,;:!?)]}").lstrip("([{\"'`")


def is_fuzzing_path(value: str) -> bool:
    if not value or not value.startswith("/"):
        return False
    if "{{" in value or "}}" in value:
        return False
    head = value.lstrip("/").split("/", 1)[0]
    if not head:
        return False
    if "." in head and head != ".well-known":
        return False
    if head in {"usr", "var", "tmp", "home", "opt", "nuclei-drupal-sa"}:
        return False
    if value.startswith(FUZZ_SUBPATH_PREFIXES):
        return True
    return any(value == prefix or value.startswith(f"{prefix}/") for prefix in FUZZ_EXACT_OR_SUBPATH)


def extract_paths(content: str) -> set[str]:
    matches = set()
    for match in BASEURL_PATH_PATTERN.findall(content):
        cleaned = normalize_match(match)
        if is_fuzzing_path(cleaned):
            matches.add(cleaned)
    for pattern in PATH_PATTERNS:
        for match in pattern.findall(content):
            cleaned = normalize_match(match)
            if is_fuzzing_path(cleaned):
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
