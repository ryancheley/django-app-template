# Contract: Instantiation Script CLI

`scripts/instantiate.py` — stdlib-only Python, runnable before any
environment setup (no uv, no venv, no dependencies).

## Invocation

```
python3 scripts/instantiate.py NEW_PROJECT_NAME
```

## Input validation (before any file is modified)

`NEW_PROJECT_NAME` must:

- match `[a-z_][a-z0-9_]*` (lowercase Python identifier shape)
- pass `str.isidentifier()`
- not be a Python keyword
- not equal `config`, `example`, or `template_project`

Any violation: exit code 2, clear message naming the rule violated, zero
files modified.

## Preconditions

- The placeholder `template_project` must be present in the repo (checked in
  pyproject.toml). If absent: exit code 3 with an "already instantiated"
  message, zero files modified. Running twice is refused, not repaired.

## Actions (single pass, in order)

1. Rewrite `template_project` → `NEW_PROJECT_NAME` in: `pyproject.toml`
   (project name/metadata), `compose.yaml` and `compose.prod.yaml` (service
   and image names), `README.md`, `CLAUDE.md`, and any other file containing
   the placeholder.
2. Remove the example app completely:
   - delete `example/` (source, migrations, templates, app-local tests)
   - remove `"example"` from `INSTALLED_APPS` in `config/settings.py`
   - remove the example include from `config/urls.py`
   - remove `example` from the coverage source list in `pyproject.toml`
3. Delete `.github/workflows/instantiation.yml`.
4. Delete `scripts/instantiate.py` itself (and `scripts/` if now empty).
5. Print next steps: copy `.env.example` → `.env`, `docker compose up`,
   `just prek-install`, verify `/health/`, run `just check`, first commit
   guidance.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Instantiation completed |
| 2 | Invalid project name (nothing modified) |
| 3 | Placeholder absent — already instantiated (nothing modified) |

## Post-conditions (asserted by tests/test_instantiation.py and instantiation.yml)

- No occurrence of `template_project` anywhere in the working tree
  (excluding `.git/`).
- No `example/` directory; no reference to `example` in
  `config/settings.py`, `config/urls.py`, or `pyproject.toml`.
- `scripts/instantiate.py` and `.github/workflows/instantiation.yml` gone.
- `just check` and `uvx prek run --all-files` pass; coverage floor holds;
  dev stack boots and `/health/` returns 200 (asserted in CI).
