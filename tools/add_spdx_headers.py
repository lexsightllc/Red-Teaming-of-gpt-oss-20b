#!/usr/bin/env python3
"""Insert SPDX-License-Identifier headers into source files."""
from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Iterable

COMMENT_STYLES = {
    ".py": "#",
    ".pyi": "#",
    ".sh": "#",
    ".bash": "#",
    ".zsh": "#",
    ".ps1": "#",
    ".psm1": "#",
    ".psd1": "#",
    ".rb": "#",
    ".pl": "#",
    ".pm": "#",
    ".t": "#",
    ".rs": "//",
    ".c": "//",
    ".h": "//",
    ".cpp": "//",
    ".hpp": "//",
    ".java": "//",
    ".cs": "//",
    ".ts": "//",
    ".tsx": "//",
    ".js": "//",
    ".jsx": "//",
    ".go": "//",
    ".gradle": "//",
    ".swift": "//",
    ".kt": "//",
    ".kts": "//",
    ".scala": "//",
    ".yml": "#",
    ".yaml": "#",
    ".toml": "#",
    ".ini": "#",
    ".cfg": "#",
    ".conf": "#",
    ".env": "#",
    ".env.example": "#",
    ".gitignore": "#",
    ".dockerignore": "#",
    ".gitattributes": "#",
    ".editorconfig": "#",
    ".gitmodules": "#",
    ".gitmessage": "#",
    ".txt": None,
    ".md": "<!-- -->",
    ".rst": "..",
    "Makefile": "#",
}

HEADER_TEXT = "SPDX-License-Identifier: MPL-2.0"

SKIP_DIRS = {".git", "__pycache__", "build", "dist", ".mypy_cache", ".pytest_cache", "sbom", "reports"}


def iter_files(paths: Iterable[pathlib.Path]) -> Iterable[pathlib.Path]:
    for path in paths:
        if path.is_dir():
            if path.name in SKIP_DIRS:
                continue
            yield from iter_files(p for p in path.iterdir())
        else:
            yield path


def comment_style_for(path: pathlib.Path, first_line: str | None = None) -> str | None:
    if path.name == "Makefile":
        return COMMENT_STYLES["Makefile"]
    ext = "".join(path.suffixes) if path.name.endswith(".env.example") else path.suffix
    if ext == "" and path.name.lower().endswith("makefile"):
        return "#"
    style = COMMENT_STYLES.get(ext)
    if style is None and not ext and first_line:
        if first_line.startswith("#!"):
            if "python" in first_line:
                return "#"
            if any(shell in first_line for shell in ("bash", "sh", "zsh")):
                return "#"
            if "powershell" in first_line or "pwsh" in first_line:
                return "#"
        if path.parent.name == "scripts":
            return "#"
    return style


def has_spdx(line: str) -> bool:
    return "SPDX-License-Identifier" in line


def insert_header(path: pathlib.Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    first_line = lines[0] if lines else None
    style = comment_style_for(path, first_line)
    if style is None:
        return
    if any(has_spdx(line) for line in lines[:5]):
        return

    header_line: str
    idx = 0

    if lines and lines[0].startswith("#!"):
        idx = 1

    if style == "<!-- -->":
        header_line = "<!-- {} -->".format(HEADER_TEXT)
    elif style == "..":
        header_line = f".. {HEADER_TEXT}"
    else:
        header_line = f"{style} {HEADER_TEXT}" if style else HEADER_TEXT

    new_lines = lines[:idx] + [header_line, ""] + lines[idx:]
    path.write_text("\n".join(new_lines) + ("\n" if lines else ""), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=pathlib.Path, default=[pathlib.Path.cwd()])
    args = parser.parse_args()

    for file_path in iter_files(args.paths):
        insert_header(file_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
