"""Post-condition tests for scripts/instantiate.py.

Structural assertions run here on a copy of the repo (fast, no Docker);
the full gate suite on an instantiated copy runs in CI
(.github/workflows/instantiation.yml). Contract:
specs/001-template-scaffold/contracts/instantiate-cli.md.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
COPY_IGNORE = shutil.ignore_patterns(
    ".git", ".venv", "bin", "staticfiles", "__pycache__", ".pytest_cache"
)


@pytest.fixture
def repo_copy(tmp_path: Path) -> Path:
    copy = tmp_path / "repo"
    shutil.copytree(REPO_ROOT, copy, ignore=COPY_IGNORE)
    return copy


def run_script(copy: Path, name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(copy / "scripts" / "instantiate.py"), name],
        capture_output=True,
        text=True,
        check=False,
    )


def tree_contains(copy: Path, needle: str) -> list[Path]:
    hits = []
    for path in copy.rglob("*"):
        if not path.is_file():
            continue
        try:
            if needle in path.read_text(encoding="utf-8"):
                hits.append(path.relative_to(copy))
        except UnicodeDecodeError:
            continue
    return hits


def test_example_app_is_not_imported_outside_itself() -> None:
    """The example app is deleted at instantiation, so nothing permanent may
    depend on it (plan: example-isolation guard)."""
    app = "example"
    needles = (f"from {app}", f"import {app}")  # built indirectly: this file must not self-match
    offenders = []
    for path in REPO_ROOT.rglob("*.py"):
        rel = path.relative_to(REPO_ROOT)
        if rel.parts[0] in {app, ".venv", "scripts"}:
            continue
        content = path.read_text(encoding="utf-8")
        if any(needle in content for needle in needles):
            offenders.append(rel)
    assert offenders == []


def test_successful_instantiation_post_conditions(repo_copy: Path) -> None:
    result = run_script(repo_copy, "acmeapp")
    assert result.returncode == 0, result.stderr

    assert tree_contains(repo_copy, "template_project") == []
    assert tree_contains(repo_copy, "template-project") == []
    assert not (repo_copy / "example").exists()
    assert not (repo_copy / "scripts" / "instantiate.py").exists()
    assert not (repo_copy / ".github" / "workflows" / "instantiation.yml").exists()

    settings = (repo_copy / "config" / "settings.py").read_text()
    urls = (repo_copy / "config" / "urls.py").read_text()
    pyproject = (repo_copy / "pyproject.toml").read_text()
    assert "example" not in settings
    assert "example" not in urls
    assert "example" not in pyproject
    assert 'name = "acmeapp"' in pyproject
    assert "include" not in urls.splitlines()[0]  # unused import removed

    compose = (repo_copy / "compose.yaml").read_text()
    assert "acmeapp" in compose


def test_invalid_name_exits_2_and_modifies_nothing(repo_copy: Path) -> None:
    before = sorted(p.relative_to(repo_copy) for p in repo_copy.rglob("*"))
    pyproject_before = (repo_copy / "pyproject.toml").read_bytes()

    for bad in ("3bad", "My-App", "class", "config", "template_project"):
        result = run_script(repo_copy, bad)
        assert result.returncode == 2, f"{bad}: {result.stderr}"

    after = sorted(p.relative_to(repo_copy) for p in repo_copy.rglob("*"))
    assert before == after
    assert (repo_copy / "pyproject.toml").read_bytes() == pyproject_before


def test_second_run_exits_3(repo_copy: Path) -> None:
    # Re-create the script after the first run consumed it: the refusal must
    # come from the missing placeholder, not the missing file.
    script_source = (repo_copy / "scripts" / "instantiate.py").read_text()
    assert run_script(repo_copy, "acmeapp").returncode == 0
    (repo_copy / "scripts").mkdir(exist_ok=True)
    (repo_copy / "scripts" / "instantiate.py").write_text(script_source)

    result = run_script(repo_copy, "otherapp")
    assert result.returncode == 3
    assert "already instantiated" in result.stderr
