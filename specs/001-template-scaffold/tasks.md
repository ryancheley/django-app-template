# Tasks: Django Application Template Scaffold

**Input**: Design documents from `/specs/001-template-scaffold/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Per Constitution Principle II, test tasks are mandatory here: the health-check integration test, the example factory-boy model test, and the instantiation post-condition test are deliverables.

**Organization**: Five hard phases matching the plan's Implementation Order, each closed by an explicit checkpoint task. **No task from a later phase may start while the predecessor phase's checkpoint task is open.** Story labels map tasks to spec user stories (US1 Fresh Start, US2 Gates, US3 Instantiation, US4 Agent/Docs); this scaffold's stories are deliberately sequential, so phases — not stories — are the execution boundaries.

**Task rules in force** (from task-shaping constraints):

- Every task produces a committable state and names its verification command. Prefer the just recipe once it exists. `just check` must never *error* on gates that already exist (failing on not-yet-built gates is acceptable; crashing is not).
- Tasks touching `pyproject.toml`, `compose.yaml`, or `justfile` are serial — never `[P]`.
- Hygiene (`.gitignore`, `.dockerignore`, prek excludes) is updated in the same task that creates the files needing it.
- Non-obvious configuration carries its rationale as a comment in the file itself (ty downgrades, port 5433, coverage floor, operator-run prod migrations) — agents reading the template never see the git log.
- Each task suggests its commit emoji (constitution: commit messages start with an emoji).

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: parallelizable (different files, no dependency on an open task)
- **[Story]**: US1–US4 for user-story-serving tasks; setup tasks unlabeled
- **Verify**: the command that defines done. **Commit**: suggested emoji.

## Path Conventions

Lodestar layout (plan.md Project Structure): apps at repo root alongside `config/`; root `tests/` for cross-app integration tests; app-local tests inside each app; `scripts/` for instantiation; `static/` for vendored assets.

---

## Phase 1: Green Baseline

**Goal**: Django skeleton, config package, health check, example app, Postgres compose, pytest passing — before any gate wiring (plan Implementation Order step 1).

- [X] T001 Create feature branch `001-template-scaffold` from `main`.
      Verify: `git branch --show-current` prints `001-template-scaffold`. Commit: 🌱
- [X] T002 Author `pyproject.toml` — project `template_project`, `requires-python = ">=3.14"`, runtime deps (Django pinned `<next-major` per research R1, psycopg, django-axes, django-csp, whitenoise, gunicorn), dev group (pytest, pytest-django, pytest-xdist, pytest-cov, factory-boy, ruff, ty) — then generate `uv.lock`. Serial (pyproject).
      Verify: `uv sync` exits 0. Commit: 📦
- [X] T003 [P] Create `.gitignore` (`.env`, `.venv/`, `bin/`, `__pycache__/`, `.pytest_cache/`, `.coverage`, `staticfiles/`) and `.dockerignore` (`.git`, `.venv`, `bin`, `.env`, caches, `specs/`).
      Verify: `git check-ignore .env .venv bin` exits 0. Commit: 🙈
- [X] T004 [P] Create `.gitleaks.toml` with an empty allowlist and a comment stating the file exists to establish the allowlist pattern.
      Verify: `uv run python -c "import tomllib,pathlib; tomllib.loads(pathlib.Path('.gitleaks.toml').read_text())"` exits 0. Commit: 🔒
- [X] T005 [P] Create `LICENSE` placeholder with a holder line the README will document as a user-action placeholder (must not trip any gate).
      Verify: `test -s LICENSE` exits 0. Commit: 📄
- [X] T006 [P] Create initial `.env.example` (SECRET_KEY, DEBUG, ALLOWED_HOSTS, POSTGRES_DB/USER/PASSWORD/HOST/PORT), one comment per variable; audited for completeness in T047.
      Verify: `test -s .env.example` exits 0. Commit: 🔧
- [X] T007 [US1] Create `manage.py`, `config/__init__.py`, `config/wsgi.py`, `config/asgi.py`.
      Verify: `uv run python -c "import config, config.wsgi, config.asgi"` exits 0. Commit: 🏗️
- [X] T008 [US1] Create example app modules per data-model.md: `example/__init__.py`, `example/apps.py`, `example/models.py` (`ExampleItem`: name, notes, created_at, updated_at, `-created_at` ordering), `example/admin.py`.
      Verify: `uv run python -m py_compile example/models.py example/admin.py example/apps.py` exits 0. Commit: 🧱
- [X] T009 [US1] Create `config/settings.py`: single env-driven module with safe-for-dev defaults (research R3); Postgres from `POSTGRES_*` env; whitenoise; django-axes (5 attempts, 1h cooloff, username+IP) and django-csp (`default-src 'self'`) with tune-per-project rationale comments (R11); SECURE_*/cookie/HSTS env-driven so prod-shaped env passes deploy checks. Serial-adjacent but single-owner file.
      Verify: `SECRET_KEY=dev-only uv run python manage.py check` exits 0. Commit: ⚙️
- [X] T010 [US1] Create `config/test_settings.py` (lodestar pattern): import settings, point DB at `localhost:5433` with an in-file comment explaining 5433 avoids colliding with a local Postgres on 5432, fast password hasher.
      Verify: `uv run python manage.py check --settings=config.test_settings` exits 0. Commit: 🧪
- [X] T011 [US1] Generate `example/migrations/0001_initial.py`.
      Verify: `SECRET_KEY=dev-only uv run python manage.py makemigrations --check --dry-run` exits 0 (no missing migrations). Commit: 🗃️
- [X] T012 [P] [US1] Create `config/views.py` with `health_check` implementing `contracts/health-endpoint.md` (SELECT 1 probe; 200 `{"status": "ok", "database": "ok"}`; 503 degraded; axes-exempt; GET only).
      Verify: `uv run python -m py_compile config/views.py` exits 0 (contract asserted by T017 tests). Commit: 🩺
- [X] T013 [P] [US1] Create `example/views.py`, `example/urls.py`, `example/templates/example/item_list.html` (extends `base.html`, semantic markup).
      Verify: `uv run python -m py_compile example/views.py example/urls.py` exits 0. Commit: 🖼️
- [X] T014 [US1] Create `config/urls.py`: admin, `/health/`, `example` include (the include is a documented removal target of instantiation).
      Verify: `SECRET_KEY=dev-only uv run python manage.py check` exits 0. Commit: 🕸️
- [X] T015 [US1] Create `templates/base.html`: semantic landmarks (header/main/footer), lang attribute, visible focus styles, `prefers-reduced-motion` respected. No static asset links yet — those land in Phase 3.
      Verify: `SECRET_KEY=dev-only uv run python manage.py check` exits 0. Commit: 📐
- [X] T016 [P] [US1] Create `example/factories.py` (`ExampleItemFactory`, Sequence-based deterministic names — no faker/random, per Principle II) plus app-local tests `example/tests/test_models.py` (factory-boy model test) and `example/tests/test_views.py` (list view renders).
      Verify: `uv run pytest example --collect-only -q` exits 0 (execution at T022). Commit: 🏭
- [X] T017 [P] [US1] Create `tests/test_health.py`: integration test asserting the 200/"ok" contract against a real database plus the 503/"degraded" path via a real broken connection — no mocks (contracts/health-endpoint.md).
      Verify: `uv run pytest tests --collect-only -q` exits 0 (execution at T022). Commit: 🧬
- [X] T018 [US1] Configure pytest in `pyproject.toml` (`DJANGO_SETTINGS_MODULE=config.test_settings`, testpaths, `-n auto`). Serial (pyproject).
      Verify: `uv run pytest --collect-only -q` exits 0. Commit: 🎛️
- [X] T019 [US1] Create multi-stage `Dockerfile` per research R7 (uv builder stage `uv sync --frozen --no-dev` → `python:3.14-slim` runtime; dev target adds dev group; shared stages for dev/prod).
      Verify: `docker build --target dev -t template_project:dev .` exits 0. Commit: 🐳
- [X] T020 [US1] Create `compose.yaml`: `web` (dev target, runserver, source bind mount, migrate-before-serve) + `db` (latest stable Postgres major per R2, named volume, healthcheck, `service_healthy` gate), host mapping 5433→5432 with the in-file rationale comment. Serial (compose.yaml).
      Verify: `docker compose config -q` exits 0. Commit: 🧩
- [X] T021 [US1] Create `compose.prod.yaml`: gunicorn, whitenoise-served collected static, `DEBUG=false`, no bind mounts, restart policies, in-file comment stating migrations are an explicit operator step in prod. Same image/stages as dev.
      Verify: `docker compose -f compose.prod.yaml config -q` exits 0. Commit: 🏭
- [X] T022 [US1] **CHECKPOINT — Phase 1 closes.** `cp .env.example .env && docker compose up -d --wait`, then all of:
      `curl -fsS localhost:8000/health/` returns `{"status": "ok", "database": "ok"}`;
      `docker compose logs 2>&1 | grep -iE "error|traceback"` returns nothing;
      `uv run pytest` green against the compose db on 5433.
      Commit: ✅

---

## Phase 2: Gates

**Goal**: ruff → ty → prek → justfile → CI → zizmor-over-that-CI, plus pip-audit, deploy-check, and the scaffold coverage floor (plan Implementation Order step 2). Blocked until T022 is closed.

- [X] T023 [US2] Configure ruff in `pyproject.toml` (line-length 100, target py314, select E F I UP B DJ) then resolve every finding across the repo. Serial (pyproject).
      Verify: `uv run ruff check . && uv run ruff format --check .` exits 0. Commit: 🧹
- [X] T024 [US2] Configure ty in `pyproject.toml`: `[tool.ty.rules]` downgrading exactly `unresolved-attribute`, `invalid-assignment`, `invalid-argument-type`, `invalid-return-type` to `warn`, with the in-file comment naming them as ty's known Django false positives to restore when ty gains Django awareness (research R4); annotate remaining code. Serial (pyproject).
      Verify: `uv run ty check` exits 0. Commit: 🔍
- [X] T025 [US2] Create `.pre-commit-config.yaml` for prek: hygiene hooks (trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-added-large-files, check-merge-conflict, detect-private-key), gitleaks, ruff check --fix + ruff format via `uv run`, ty via `uv run`, zizmor via pinned `uvx` on workflow files; excludes cover vendored `static/` where appropriate.
      Verify: `uvx prek@<pinned> run --all-files` exits 0. Commit: 🪝
- [X] T026 [US2] Create `justfile` implementing `contracts/justfile-recipes.md`: every constitutional recipe plus `tailwind-install`, `tailwind`, `htmx-update`; tool versions and checksums pinned once as top-level variables (R6/R8/R9); one-line comment above each recipe stating what it does and which CI job it mirrors; POSIX-sh portable throughout. Serial (justfile).
      Verify: `just --list` exits 0, then `just lint && just typecheck` exits 0. Commit: 🤖
- [X] T027 [US2] Create `.github/workflows/ci.yml` per research R12: `uv sync --frozen`; lint, format check, ty, coverage-gated pytest with Postgres service container, pip-audit, deploy-check, zizmor; every action pinned by full SHA with a version comment; least-privilege `permissions:`.
      Verify: `uvx prek@<pinned> run --files .github/workflows/ci.yml` exits 0. Commit: 🚀
- [X] T028 [P] [US2] Run zizmor over the workflows and fix every finding. Depends on T027 only; parallel-safe against T029/T030.
      Verify: `just zizmor` exits 0. Commit: 🛡️
- [X] T029 [P] [US2] Make the dependency audit gate green; any ignore carries an inline reason plus review date per the constitution. Parallel-safe against T028/T030.
      Verify: `just audit` exits 0. Commit: 🔎
- [X] T030 [P] [US2] Make the deploy check green with prod-shaped env (`DEBUG=false`, real `config.settings`): fix any SECURE_*/cookie/HSTS findings in `config/settings.py`. Parallel-safe against T028/T029.
      Verify: `just deploy-check` exits 0. Commit: 🔐
- [X] T031 [P] [US2] Create `.github/dependabot.yml` (uv + github-actions ecosystems).
      Verify: `uvx prek@<pinned> run --files .github/dependabot.yml` exits 0. Commit: 🤝
- [X] T032 [US2] Coverage floor, measurement one of two (linked to T045): measure scaffold coverage over sources `config` + `example`, set `--cov-fail-under` to the measured floor in `pyproject.toml` with an in-file comment stating the floor is measured-not-aspirational, ratchets upward only, and is re-verified post-instantiation (research R5 step 1). Depends on T016, T017, T018, T023–T025. Serial (pyproject).
      Verify: `just cov` exits 0. Commit: 📊
- [X] T033 [US2] **CHECKPOINT — Phase 2 closes.** All of:
      `just check` exits 0 (lint → typecheck → zizmor → cov);
      `uvx prek@<pinned> run --all-files` exits 0;
      `git push -u origin 001-template-scaffold` then `gh run watch --exit-status` shows `ci.yml` green.
      Commit: ✅

---

## Phase 3: Frontend

**Goal**: Vendored htmx, Tailwind standalone CLI recipes, committed compiled stylesheet, wired base template — born gated (plan Implementation Order step 3). Blocked until T033 is closed.

- [ ] T034 [US1] Vendor htmx: run `just htmx-update` (downloads pinned 2.x, verifies SHA-256, writes `static/js/htmx.min.js` per research R9); commit the vendored file; confirm prek excludes/large-file settings accommodate it in the same task.
      Verify: `test -s static/js/htmx.min.js && uvx prek@<pinned> run --all-files` exits 0. Commit: ⚡
- [ ] T035 [US1] Install the Tailwind CLI via `just tailwind-install` (pinned version, SHA-256 verified, lands in gitignored `bin/` per research R8) then create `static/css/input.css` (v4 CSS-first: `@import "tailwindcss"` + `@source` directives).
      Verify: `test -x bin/tailwindcss && test -s static/css/input.css` exits 0. Commit: 🎨
- [ ] T036 [US1] Build the committed stylesheet: run `just tailwind`, commit `static/css/tailwind.css`; adjust prek excludes for the generated file in the same task if hooks flag it.
      Verify: `test -s static/css/tailwind.css && uvx prek@<pinned> run --all-files` exits 0. Commit: 💅
- [ ] T037 [US1] Wire `templates/base.html` to the compiled stylesheet plus vendored htmx via `{% static %}`.
      Verify: `uv run pytest tests/test_health.py example` exits 0 (pages render with wired assets). Commit: 🔌
- [ ] T038 [US1] Style `example/templates/example/item_list.html` with Tailwind utilities meeting Principle IV (4.5:1 contrast, visible focus, no color-only meaning) plus one minimal htmx interaction demonstrating the pattern; extend `example/tests/test_views.py` to assert the htmx endpoint responds.
      Verify: `uv run pytest example` exits 0. Commit: ✨
- [ ] T039 [US1] **CHECKPOINT — Phase 3 closes.** All of:
      `just check` exits 0;
      `docker compose up -d --wait && curl -fsS localhost:8000/` returns the styled page (`curl -fsS localhost:8000/ | grep -q tailwind.css` and `grep -q htmx`);
      `uv run pytest` green.
      Commit: ✅

---

## Phase 4: Instantiation

**Goal**: The script, its tests, `instantiation.yml`, the example-isolation grep — landing last, once every reference the script rewrites or removes is final (plan Implementation Order step 4). Blocked until T039 is closed.

- [ ] T040 [US3] Write `scripts/instantiate.py` implementing `contracts/instantiate-cli.md`: stdlib-only; name validation before any mutation (exit 2); already-instantiated refusal (exit 3); single-pass `template_project` rewrite (pyproject, compose files, README.md, CLAUDE.md); complete `example/` removal (directory, INSTALLED_APPS, urls include, coverage source entry); self-deletion plus `.github/workflows/instantiation.yml` deletion; next-steps output.
      Verify: `python3 scripts/instantiate.py --help` exits 0 and `python3 scripts/instantiate.py 3bad; test $? -eq 2` holds with `git status --porcelain` empty. Commit: 🛠️
- [ ] T041 [P] [US3] Write `tests/test_instantiation.py`: copy repo to a tmp dir, run the script, assert every CLI-contract post-condition (no `template_project`, no `example/`, no example references in settings/urls/pyproject, script + workflow gone); assert exit 2 on invalid name with zero modifications; assert exit 3 on second run; include the example-isolation guard — no `example` imports outside `example/` (research R14/R15).
      Verify: `uv run pytest tests/test_instantiation.py` exits 0. Commit: 🧪
- [ ] T042 [P] [US3] Create `.github/workflows/instantiation.yml` per research R12/R15: checkout, `python3 scripts/instantiate.py testproject`, then the full gate suite on the result (`uv sync --frozen`, ruff, ty, coverage-gated pytest with Postgres service) plus the example-import grep guard; SHA-pinned actions, least permissions.
      Verify: `just zizmor` exits 0 (now covering both workflows). Commit: 🔁
- [ ] T043 [US3] Coverage floor, measurement two of two (linked to T032): run the instantiation dry-run on a repo copy, measure coverage there, set the final `--cov-fail-under` in `pyproject.toml` to the lower of the two measurements per research R5 (update the in-file comment with both numbers). Serial (pyproject).
      Verify: `just cov` exits 0 in the template repo AND `uv run pytest --cov=config --cov-fail-under=<floor>` exits 0 inside the instantiated copy. Commit: 📊
- [ ] T044 [US3] **CHECKPOINT — Phase 4 closes.** Scripted dry run, all commands exiting 0:
      `git clone . /tmp/inst-check && cd /tmp/inst-check && python3 scripts/instantiate.py checkproject`;
      `grep -r template_project . --exclude-dir=.git` returns nothing; `test ! -d example`;
      `uv sync && just check` green in the copy;
      `cp .env.example .env && docker compose up -d --wait && curl -fsS localhost:8000/health/` returns 200 "ok" in the copy;
      back in the template repo: `just check` and `uv run pytest` still green; `git push` then `gh run watch --exit-status` green on both workflows.
      Commit: ✅

---

## Phase 5: Documentation

**Goal**: README five-minute path, CLAUDE.md, `.env.example` audit — describing finished behavior only. Blocked until T044 is closed.

- [ ] T045 [US4] Write `README.md`: five-minute clone-to-running-site path, instantiation instructions, recipe table, every user-action placeholder documented (project name, LICENSE holder) per spec FR-011/FR-018.
      Verify: `uvx prek@<pinned> run --files README.md` exits 0 and `grep -q "instantiate" README.md && grep -q "LICENSE" README.md` exits 0. Commit: 📖
- [ ] T046 [P] [US4] Rewrite `CLAUDE.md` (preserving the SPECKIT marker block): project layout, every just recipe, gate expectations, the rule that `just check` runs before every push.
      Verify: `uvx prek@<pinned> run --files CLAUDE.md` exits 0 and `grep -q "just check" CLAUDE.md` exits 0. Commit: 🤖
- [ ] T047 [US4] Audit `.env.example` against both compose files: extract every `${VAR}`/`env_file` variable read by `compose.yaml` and `compose.prod.yaml`, diff against `.env.example` keys, reconcile.
      Verify: `uv run python -c "<extract-and-diff one-liner>"` exits 0 with an empty diff. Commit: 🔧
- [ ] T048 [US4] **CHECKPOINT — Phase 5 closes (feature done).** Scripted fresh-clone walkthrough following only README commands:
      `git clone . /tmp/readme-walkthrough && cd /tmp/readme-walkthrough` then execute the README's quickstart lines verbatim (`cp .env.example .env`, `docker compose up -d --wait`, health curl, `just check`), all exiting 0;
      `grep -rn "TODO\|FIXME" --exclude-dir=.git --exclude-dir=.specify --exclude-dir=specs .` returns nothing (spec SC-007);
      `git push` then `gh pr create` and `gh pr checks --watch` all green — squash-merge, switch to main, pull, per the constitution.
      Commit: ✅

---

## Dependencies

- **Hard phase gates**: T022 → Phase 2, T033 → Phase 3, T039 → Phase 4, T044 → Phase 5. A checkpoint task open = its successor phase closed.
- **Coverage floor pair**: T032 (scaffold measurement) depends on every Phase 1/2 test-adjacent task (T016, T017, T018, T023–T025); T043 (post-instantiation measurement) depends on T032, T040, T041 and finalizes the number. Two linked tasks by design — never one.
- **zizmor**: T028 depends on T027 only; runs parallel with T029 (audit) and T030 (deploy-check).
- **Serial files**: `pyproject.toml` (T002, T018, T023, T024, T032, T043), `compose.yaml` (T020), `justfile` (T026) — no `[P]` marker ever appears on tasks touching these.
- T040 must land after every file it rewrites or removes reaches final form — which is what the phase ordering guarantees.

## Parallel Execution Examples

- Phase 1: T003, T004, T005, T006 together after T002; T012, T013 after T009; T016, T017 after T011/T015.
- Phase 2: T028, T029, T030, T031 concurrently once T026/T027 exist.
- Phase 4: T041 and T042 concurrently once T040 is written.
- Phase 5: T046 alongside T045.

## Implementation Strategy

**MVP**: Phase 1 (T001–T022) — a booting, health-checked, pytest-green dev stack — validated at the checkpoint before any gate wiring.

**Incremental delivery**: each phase ends in a committable, checkpoint-verified state; every acceptance statement in this file is a command or a test, and the checkpoint commands are the phase's definition of done.

**Version resolution discipline**: every "pinned"/"latest at implementation time" value (Django floor, Postgres major, prek/zizmor/pip-audit versions, Tailwind CLI + checksum, htmx + checksum) is resolved by checking upstream at the moment its task executes — never guessed from memory (research R1, R2, R6, R8, R9). Where this file writes `uvx prek@<pinned>`, the pin chosen in T026's justfile variables is the single source for all later tasks.
