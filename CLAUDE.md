# template_project

Django application template. Constitution (binding):
`.specify/memory/constitution.md`.

## Layout

- `config/` — Django project package (settings, urls, wsgi/asgi, health
  check view). Permanent: survives instantiation.
- `example/` — demonstrates the expected app layout (models, factories,
  views, urls, templates, app-local `tests/`). Deleted by
  `scripts/instantiate.py`; nothing outside it may import from it.
- `templates/base.html` — semantic, accessible base wired to the committed
  Tailwind stylesheet and vendored htmx.
- `static/` — `css/input.css` (Tailwind v4 CSS-first source),
  `css/tailwind.css` (committed build output), `js/htmx.min.js` (vendored,
  checksum-pinned in the justfile).
- `tests/` — cross-app integration tests (health check, instantiation).
- `scripts/instantiate.py` — one-shot project rename + example-app removal.
- `compose.yaml` dev / `compose.prod.yaml` reference prod; shared Dockerfile
  stages.

## Commands

All developer tasks run through the justfile (`just --list` for everything):

- `just up` / `just down` — dev stack; web waits on the db healthcheck; dev
  applies migrations on start.
- `just test` / `just test-fast` — pytest via `config/test_settings.py`;
  host-side runs hit the compose db on `localhost:5433` (override with
  `POSTGRES_PORT` if you remapped `POSTGRES_HOST_PORT`).
- `just check` — lint → typecheck → zizmor → coverage-gated tests.
  **Non-negotiable: run and pass before every push.**
- `just prek` / `just prek-install` — local hooks; they mirror CI, CI is
  authoritative.
- `just tailwind` — rebuild the committed stylesheet after template edits.

## Gate expectations

- ruff check + `ruff format --check` must be clean; ty must pass
  (`--exit-zero-on-warning`; the four Django false-positive rules are
  downgraded to warn in `pyproject.toml` with rationale).
- Coverage floor in `pyproject.toml` is measured and only ratchets upward.
- Workflows are SHA-pinned and zizmor-clean; pip-audit fails closed;
  `manage.py check --deploy --fail-level WARNING` passes with DEBUG=false.
- No secrets in the repo; config comes from `.env` (see `.env.example`).
- New code is fully type-annotated; every feature ships an integration
  test; bug fixes ship a regression test that failed before the fix.

## Workflow

Feature branches only — never commit to main. Emoji-prefixed commit
messages. PRs squash-merge once green; then switch to main and pull.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/001-template-scaffold/plan.md` (research, data model, contracts, and
quickstart live alongside it in `specs/001-template-scaffold/`).
<!-- SPECKIT END -->
