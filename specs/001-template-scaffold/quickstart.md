# Quickstart Validation: Django Application Template Scaffold

Runnable scenarios proving the feature works end-to-end. Each maps to a spec
user story. Contracts referenced: [health-endpoint](contracts/health-endpoint.md),
[instantiate-cli](contracts/instantiate-cli.md),
[justfile-recipes](contracts/justfile-recipes.md).

## Prerequisites

- Docker with Compose v2
- uv (and uvx) installed
- just installed
- No local service already bound to host ports 8000 or 5433

## Scenario 1 — Fresh start (US1, SC-001)

```sh
git clone <template-repo> demo && cd demo
cp .env.example .env
docker compose up -d --wait
curl -s localhost:8000/health/
```

**Expected**: within five minutes on a warm Docker cache, the health check
returns `{"status": "ok", "database": "ok"}` with HTTP 200; migrations were
applied by the dev entrypoint; `docker compose logs` shows zero errors.

## Scenario 2 — Gates green on the untouched scaffold (US2, SC-002/003)

```sh
uvx prek@<pinned> run --all-files   # or: just prek
just check                          # lint → typecheck → zizmor → cov
```

**Expected**: every hook passes; the aggregate check passes including the
coverage floor. No shipped file trips hygiene, gitleaks, ruff, ty, or
zizmor.

## Scenario 3 — First push CI (US2, SC-004)

```sh
gh repo create demo --private --source . --push
gh run watch
```

**Expected**: `ci.yml` completes green (lint, format, ty, coverage-gated
pytest against the Postgres service, pip-audit, deploy-check, zizmor) and
`instantiation.yml` completes green — with zero repository configuration
beyond creation (no secrets, no settings).

## Scenario 4 — Instantiation (US3, SC-005/006)

```sh
python3 scripts/instantiate.py myproject
grep -r template_project . --exclude-dir=.git   # expect: no matches
test ! -d example                                # expect: gone
just check
uvx prek@<pinned> run --all-files
docker compose up -d --wait && curl -s localhost:8000/health/
```

**Expected**: rename applied everywhere; example app and all references
removed; script and `instantiation.yml` deleted themselves; all gates green;
coverage floor still holds; health check returns 200. Negative cases per the
CLI contract: an invalid name (`3bad`, `My-App`) exits 2 touching nothing; a
second run exits 3 with "already instantiated".

## Scenario 5 — Agent and Speckit readiness (US4)

```sh
cat CLAUDE.md          # layout, recipes, gate expectations, pre-push rule
ls .specify/memory/constitution.md
```

**Expected**: CLAUDE.md alone is sufficient for an agent to run, test, and
gate its work; the ratified constitution and Speckit templates/commands are
present so `/speckit.plan`'s Constitution Check needs no setup.

## Accessibility spot-check (Principle IV)

With the dev stack up, the example page and base template must show:
semantic landmarks (header/main/footer), visible keyboard focus on every
interactive element, no color-only meaning, contrast ≥ 4.5:1 for body text,
and no motion that ignores `prefers-reduced-motion`.
