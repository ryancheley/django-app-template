# Implementation Plan: Django Application Template Scaffold

**Branch**: `001-template-scaffold` | **Date**: 2026-07-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-template-scaffold/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build the template repository itself: a minimal but real Django project
(`template_project` placeholder identity, `config` package, disposable
`example` app) that boots with `docker compose up`, passes every
constitutional gate untouched, and converts into a real project via a
stdlib-only instantiation script that renames the project, removes the
example app, and leaves all gates green. Implementation follows a strict
order: green Django baseline first, then gates in dependency order (ruff/ty →
prek → justfile → CI → zizmor over that CI), then Tailwind/htmx wiring born
gated, then the instantiation script last once every reference it rewrites is
final. Where a decision is not settled below, the pattern proven in lodestar
wins over inventing a new one.

## Technical Context

**Language/Version**: Python 3.14 (all code targets it; no newer syntax/stdlib)

**Primary Dependencies**: Django (latest stable at implementation, pinned
`<next-major`), psycopg, django-axes, django-csp, whitenoise, gunicorn;
dev group: pytest, pytest-django, pytest-xdist, pytest-cov, factory-boy,
ruff, ty

**Storage**: PostgreSQL (latest stable major in compose; host port 5433 to
avoid colliding with a local 5432, per lodestar convention)

**Testing**: pytest + pytest-django via `config/test_settings.py`;
pytest-xdist parallel; pytest-cov with ratcheting floor measured during
implementation and verified in both scaffold states

**Target Platform**: Docker Compose (dev: runserver + bind mounts; prod
reference: gunicorn + whitenoise, DEBUG off); GitHub Actions default runners
for CI

**Project Type**: Web application template repository (apps at repo root
alongside `config/` — lodestar layout, not `src/`)

**Performance Goals**: Clone-to-running-site under five minutes on a warm
Docker cache; no other performance targets — this is scaffolding, not a
product

**Constraints**: Repo must be runnable and gate-testable exactly as
committed (no templating syntax); instantiation script is stdlib-only Python
runnable before any environment setup; justfile recipes POSIX-sh portable
(no fish syntax, no bashisms); no Node toolchain (Tailwind standalone CLI);
no runtime CDNs (htmx vendored)

**Scale/Scope**: ~40 shipped files; two apps (`config` permanent, `example`
disposable); two compose files; two CI workflows; one instantiation script

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Section | Requirement | Plan compliance |
|---------------------|-------------|-----------------|
| I. Code Quality | ruff check + format, ty clean, full annotations, documented ty Django downgrades only | PASS — pyproject configures ruff (line-length 100, py314, E F I UP B DJ) and ty with exactly the four constitutional downgrades, each commented; all scaffold code fully annotated |
| II. Testing Standards | pytest/pytest-django/xdist/cov, factory-boy, real objects, integration test per feature, deterministic | PASS — health-check integration test (permanent), example model test via factory-boy (disposable), instantiation post-condition test; no mocks anywhere (no external services exist); floor measured then enforced |
| III. Security by Default | gitleaks, zizmor (pinned, regular persona), pip-audit fail-closed, deploy check gate, axes + csp | PASS — all five ship wired into prek and CI; `.gitleaks.toml` empty allowlist; actions SHA-pinned; deploy-check runs real settings with DEBUG off |
| IV. Accessibility | WCAG 2.1 AA blocking at all phases | PASS — scaffold UI surface is one base template + example page: semantic HTML, visible focus, contrast-checked Tailwind palette, prefers-reduced-motion respected; contract recorded in quickstart validation |
| V. Simplicity & Reproducibility | Django built-ins first, every dep justified, compose-up reproducibility, vendored assets | PASS — dependency list is exactly the constitution's named set (see Complexity Tracking: empty); fresh clone → `docker compose up`; htmx vendored + pinned, Tailwind CLI pinned with verify recipe |
| Technology Stack | Py 3.14, Django LTS+, Postgres/psycopg, uv/uvx, Docker×2 compose, Tailwind, htmx | PASS — matches exactly; uv.lock is tool-version source of truth; prek/zizmor/pip-audit via pinned uvx, intentionally not project deps |
| Tooling & Automation | justfile recipes, prek hook set, CI mirrors local | PASS — all required recipes plus `tailwind`/`tailwind-install`; hook set complete; ci.yml runs the same gates plus cov/audit/deploy-check |
| Development Workflow | feature branch, `just check` pre-push, squash merge | PASS — work happens on `001-template-scaffold`; CLAUDE.md records the pre-push rule |

**Initial evaluation**: PASS, no violations to justify.

**Post-design re-evaluation** (after Phase 1): PASS — design artifacts
introduce no new dependencies and no deviations. Complexity Tracking remains
empty.

**Plan-specific guard**: the example app must not become load-bearing. A CI
step (and local check inside the instantiation test) greps for imports of
`example` outside `example/` itself and fails if any exist.

## Project Structure

### Documentation (this feature)

```text
specs/001-template-scaffold/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── health-endpoint.md
│   ├── instantiate-cli.md
│   └── justfile-recipes.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
.
├── .github/
│   ├── workflows/
│   │   ├── ci.yml               # lint, format, ty, cov-gated pytest (pg service), pip-audit, deploy-check, zizmor
│   │   └── instantiation.yml    # run instantiate.py with test name, full gate suite on result; deleted by the script
│   └── dependabot.yml           # uv + github-actions ecosystems
├── .specify/                    # Speckit chain (constitution ratified at memory/constitution.md)
├── config/                      # Permanent Django project package (survives instantiation)
│   ├── __init__.py
│   ├── settings.py              # single env-driven settings module, safe-for-dev defaults
│   ├── test_settings.py         # pytest overrides (lodestar pattern)
│   ├── urls.py                  # includes /health/ and example app include (removed at instantiation)
│   ├── views.py                 # health_check view with DB probe
│   ├── wsgi.py
│   └── asgi.py
├── example/                     # Disposable example app (removed at instantiation)
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── models.py                # one small model demonstrating conventions
│   ├── factories.py             # factory-boy factory
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   ├── templates/example/       # app-namespaced templates
│   └── tests/                   # app-local tests incl. factory-boy model test
├── templates/
│   └── base.html                # permanent base: vendored htmx + compiled Tailwind wired in
├── static/
│   ├── css/
│   │   ├── input.css            # Tailwind input stylesheet
│   │   └── tailwind.css         # committed compiled output
│   └── js/
│       └── htmx.min.js          # vendored, pinned
├── tests/                       # cross-app integration tests (permanent)
│   ├── test_health.py           # integration test hitting /health/
│   └── test_instantiation.py    # runs instantiate.py on a repo copy, asserts post-conditions
├── scripts/
│   └── instantiate.py           # stdlib-only; deletes itself + instantiation.yml when done
├── bin/                         # gitignored; tailwind-install target
├── manage.py
├── Dockerfile                   # multi-stage, ghcr.io/astral-sh/uv pattern, shared dev/prod stages
├── compose.yaml                 # dev: web (runserver, bind mount) + db (pg, healthcheck, host 5433)
├── compose.prod.yaml            # reference prod: gunicorn, whitenoise, DEBUG off, no mounts
├── justfile                     # all constitutional recipes + tailwind, tailwind-install
├── .pre-commit-config.yaml      # prek hook set per constitution
├── pyproject.toml               # uv-managed; ruff, ty, coverage, pytest config
├── uv.lock
├── .env.example                 # every variable either compose file reads
├── .gitignore
├── .dockerignore
├── .gitleaks.toml               # empty allowlist, pattern established
├── LICENSE                      # placeholder, documented in README
├── README.md                    # five-minute path; all user-action placeholders listed
└── CLAUDE.md                    # layout, recipes, gate expectations, just-check-before-push rule
```

**Structure Decision**: lodestar layout — Django apps at the repository root
next to `config/`, root-level `tests/` for cross-app integration tests,
app-local tests inside each app. No `src/` indirection. Permanent surfaces
(health check, base template, root tests) live in `config/`, `templates/`,
and `tests/`; everything under `example/` is disposable by construction and
guarded by the no-imports-from-example check.

## Implementation Order

Settled ordering constraints (violating these creates ungated or unrenameable
work):

1. **Green baseline**: Django skeleton (`config`, `example`, health check,
   pytest passing) before any gate wiring.
2. **Gates in dependency order**: ruff + ty config → prek config → justfile →
   CI workflows → zizmor run over the CI just created.
3. **Frontend born gated**: Tailwind CLI recipe, vendored htmx, base template
   wiring only after the gates exist.
4. **Instantiation last**: `scripts/instantiate.py` and `instantiation.yml`
   land in one change, once every reference the script rewrites or removes is
   final. Coverage floor finalized only after post-instantiation verification.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Every dependency in the plan is named by the constitution
(Technology Stack, Tooling, or Security sections); no additional packages,
no structural deviations. Table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
