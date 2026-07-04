#!/usr/bin/env python3
"""Instantiate a real project from this template.

Stdlib only — runs before any environment setup:

    python3 scripts/instantiate.py my_new_project

In one pass this script:
  1. rewrites the ``template_project`` placeholder everywhere it appears
     (pyproject metadata, uv.lock, compose project/image names, docs);
  2. removes the ``example`` app and every reference to it;
  3. deletes its own CI workflow and then itself.

Contract: specs/001-template-scaffold/contracts/instantiate-cli.md.
Exit codes: 0 success, 2 invalid name, 3 already instantiated.
"""

import argparse
import keyword
import re
import shutil
import sys
from pathlib import Path

PLACEHOLDER = "template_project"
# uv normalizes underscores to hyphens in uv.lock's package name.
PLACEHOLDER_NORMALIZED = "template-project"
RESERVED_NAMES = {"config", "example", PLACEHOLDER}
NAME_RE = re.compile(r"^[a-z_][a-z0-9_]*$")

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "bin", "staticfiles", "__pycache__", ".pytest_cache"}

EXAMPLE_APP_DIR = REPO_ROOT / "example"
SELF = REPO_ROOT / "scripts" / "instantiate.py"
OWN_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "instantiation.yml"


def fail(message: str, code: int) -> int:
    print(f"error: {message}", file=sys.stderr)
    return code


def validate_name(name: str) -> str | None:
    """Return an error message, or None if the name is acceptable."""
    if not NAME_RE.match(name):
        return f"{name!r} must match [a-z_][a-z0-9_]* (lowercase identifier)"
    if not name.isidentifier():
        return f"{name!r} is not a valid Python identifier"
    if keyword.iskeyword(name):
        return f"{name!r} is a Python keyword"
    if name in RESERVED_NAMES:
        return f"{name!r} is reserved by the template"
    return None


def text_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(REPO_ROOT).parts):
            continue
        files.append(path)
    return files


def rewrite_placeholder(new_name: str) -> int:
    """Replace the placeholder (both spellings) in every text file."""
    normalized = new_name.replace("_", "-")
    changed = 0
    for path in text_files():
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary (vendored assets, images)
        updated = content.replace(PLACEHOLDER, new_name).replace(
            PLACEHOLDER_NORMALIZED, normalized
        )
        if updated != content:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def remove_example_references() -> None:
    """Drop the example app directory and every wiring point that names it."""
    shutil.rmtree(EXAMPLE_APP_DIR)

    settings = REPO_ROOT / "config" / "settings.py"
    settings.write_text(
        "".join(
            line
            for line in settings.read_text(encoding="utf-8").splitlines(keepends=True)
            if line.strip() not in {'"example",', "# Apps"}
        ),
        encoding="utf-8",
    )

    urls = REPO_ROOT / "config" / "urls.py"
    urls_content = urls.read_text(encoding="utf-8")
    urls_content = urls_content.replace(
        "from django.urls import include, path", "from django.urls import path"
    )
    urls.write_text(
        "".join(
            line
            for line in urls_content.splitlines(keepends=True)
            if "example" not in line
        ),
        encoding="utf-8",
    )

    pyproject = REPO_ROOT / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    content = content.replace('source = ["config", "example"]', 'source = ["config"]')
    content = content.replace('testpaths = ["tests", "example"]', 'testpaths = ["tests"]')
    pyproject.write_text(content, encoding="utf-8")

    tailwind_input = REPO_ROOT / "static" / "css" / "input.css"
    tailwind_input.write_text(
        "".join(
            line
            for line in tailwind_input.read_text(encoding="utf-8").splitlines(keepends=True)
            if "example" not in line
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("name", help="new project name (lowercase Python identifier)")
    args = parser.parse_args()

    error = validate_name(args.name)
    if error is not None:
        return fail(error, 2)

    pyproject = REPO_ROOT / "pyproject.toml"
    if f'name = "{PLACEHOLDER}"' not in pyproject.read_text(encoding="utf-8"):
        return fail(
            "already instantiated: the template_project placeholder is gone. "
            "This script runs exactly once.",
            3,
        )

    changed = rewrite_placeholder(args.name)
    remove_example_references()
    if OWN_WORKFLOW.exists():
        OWN_WORKFLOW.unlink()
    SELF.unlink()
    if not any(SELF.parent.iterdir()):
        SELF.parent.rmdir()

    print(f"Instantiated {args.name!r}: rewrote {changed} files, removed the example app.")
    print("Next steps:")
    print("  1. cp .env.example .env   # then edit values")
    print("  2. docker compose up -d --wait")
    print("  3. curl localhost:8000/health/   # expect status ok")
    print("  4. just prek-install")
    print("  5. just check             # run before every push")
    print("  6. Review README.md placeholders (LICENSE holder), commit, and start building.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
