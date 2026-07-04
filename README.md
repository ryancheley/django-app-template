# template_project

A reusable Django application template: the fully gated starting point for
new Django apps and sites. Fresh clone to running site in one command; every
quality gate green on the untouched scaffold.

Stack: Python 3.14, Django, PostgreSQL, uv, Docker Compose, Tailwind
(standalone CLI, no Node), vendored htmx. Governance lives in
`.specify/memory/constitution.md`.

## Five minutes to a running site

```sh
git clone <this-repo> myproject && cd myproject
cp .env.example .env
docker compose up -d --wait
curl localhost:8000/health/    # {"status": "ok", "database": "ok"}
```

The dev stack applies migrations before serving. The example app's page is
at `http://localhost:8000/`. If ports 8000/5433 are taken on your machine,
set `WEB_PORT` / `POSTGRES_HOST_PORT` in `.env`.

## Starting a real project

```sh
python3 scripts/instantiate.py my_new_project
```

One pass, stdlib only, runs before any environment setup. It renames
`template_project` everywhere (pyproject, uv.lock, compose project and image
names, docs), removes the `example` app and every reference to it, deletes
its own CI workflow and test, then prints next steps. It refuses invalid
names (exit 2) and refuses to run twice (exit 3). All gates stay green
afterward — CI proves this on every push via `instantiation.yml`.

## Placeholders that need your action

| Placeholder | Where | What to do |
|-------------|-------|------------|
| `template_project` | everywhere | replaced by `scripts/instantiate.py` |
| `LICENSE HOLDER` | `LICENSE` | put your name in the copyright line |

Neither placeholder fails any gate; both are safe to leave while exploring.

## Developer tasks

Everything runs through [just](https://just.systems). The full list is in
the `justfile`; the ones you will use daily:

| Recipe | What it does |
|--------|--------------|
| `just up` / `just down` | start/stop the dev compose stack |
| `just test` / `just test-fast` | full suite / reuse-db inner loop |
| `just check` | lint → typecheck → zizmor → coverage-gated tests. **Run before every push.** |
| `just prek-install` | install the git hooks (once per clone) |
| `just tailwind` | rebuild the committed stylesheet |

Host-side tests reach the compose database on `localhost:5433`.

## Quality gates

Local prek hooks mirror CI; CI is authoritative and is green on first push
with zero repository configuration. The gates: ruff (lint + format), ty
(type check), gitleaks (secrets), zizmor (workflow audit, actions pinned by
SHA), pip-audit (fail-closed), the coverage-floored pytest suite, and
Django's deploy checks against the real settings module with `DEBUG=false`.

The coverage floor in `pyproject.toml` is measured, not aspirational — it
only ratchets upward.

## Working with Speckit and Claude Code

The ratified constitution and the Speckit templates ship in `.specify/`, so
the specify → plan → tasks → implement chain works immediately. `CLAUDE.md`
tells coding agents how to run, test, and gate their work.
