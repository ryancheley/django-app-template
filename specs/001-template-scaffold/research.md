# Phase 0 Research: Django Application Template Scaffold

No NEEDS CLARIFICATION markers survived Technical Context — the feature input
settled every scope-level decision. This document records the remaining
technology-level decisions, their rationale, and the alternatives rejected.
Where a decision defers a concrete number/version to implementation time,
the resolution *procedure* is recorded so the implementing task has no
discretion left.

## R1. Django version and pin strategy

- **Decision**: Latest stable Django at implementation time, constrained
  `Django>=<latest>,<next-major>` in pyproject (e.g. `>=6.0,<7.0` if 6.0 is
  current at implementation). Exact floor set by the implementing task after
  checking PyPI; uv.lock records the resolved version.
- **Rationale**: Constitution requires "current LTS or newer at template
  instantiation"; the feature input settles "latest stable with a
  `<next-major` upper bound". The upper bound prevents a silent major jump
  via Dependabot while letting feature releases flow.
- **Alternatives considered**: Pinning to the LTS only — rejected because the
  template instantiates new projects that should start current; exact `==`
  pin — rejected because uv.lock already provides exactness and `==` in
  pyproject fights Dependabot.

## R2. PostgreSQL major and connection topology

- **Decision**: Latest stable Postgres major as the compose image (verify at
  implementation; 18 expected), named volume, container healthcheck, web
  waits on `service_healthy`. Host port mapping **5433→5432** so host-side
  pytest reaches it without colliding with a local Postgres on 5432.
- **Rationale**: Lodestar convention, encoded in the justfile's test recipes;
  templates should start on the newest major since they have no legacy data.
- **Alternatives considered**: Matching a hosting provider's default major —
  rejected as premature (deployment is out of scope); SQLite for tests —
  rejected because tests must run against the production database engine
  (parity, Postgres-specific behavior).

## R3. Settings shape

- **Decision**: Single `config/settings.py` driven by environment variables
  with safe-for-dev defaults, plus `config/test_settings.py` importing and
  overriding for pytest. No base/dev/prod settings package.
- **Rationale**: Lodestar pattern; the constitution's dev/prod parity is
  enforced through env vars, and the deploy-check gate exercises the *real*
  settings module with `DEBUG=false`, which a split-module layout would
  bypass.
- **Alternatives considered**: `settings/` package with base/dev/prod —
  rejected per explicit feature input (parity via env vars, one real module);
  django-environ — rejected: `os.environ` plus small helpers is stdlib-only
  and one less dependency (Principle V).

## R4. ty configuration and the four Django downgrades

- **Decision**: `[tool.ty.rules]` in pyproject downgrades exactly
  `unresolved-attribute`, `invalid-assignment`, `invalid-argument-type`,
  `invalid-return-type` to `warn`, with one comment block explaining these
  are ty's known Django false positives (ORM/manager magic) to be restored
  when ty gains Django awareness. All other rules stay at default severity.
  ty runs via `uv run ty check` so uv.lock governs its version.
- **Rationale**: Constitution names precisely these four; `warn` keeps the
  findings visible in output without failing the gate, which "ignore" would
  hide entirely.
- **Alternatives considered**: `ignore` severity — rejected (hides real
  regressions in those categories); per-line `# type: ignore` — rejected
  (would smear dozens of justification comments across model/view code).

## R5. Coverage floor procedure

- **Decision**: Three-step procedure executed as its own implementation task:
  (1) measure coverage on the finished untouched scaffold, (2) run the
  instantiation script on a copy and measure again, (3) set
  `--cov-fail-under` to the *lower* of the two measurements rounded down to
  the nearest whole percent. Coverage sources are `config` and `example`;
  the instantiation script drops `example` from the list.
- **Rationale**: The floor must hold in both shipped states (spec FR-021);
  measuring both before finalizing is the only way to guarantee that. The
  constitution's ratchet ("upward, never downward") starts from a true
  number, not a guess.
- **Alternatives considered**: Fixed 80/90% target — rejected: either
  unreachable on a tiny scaffold (blocks ship) or trivially low (meaningless
  ratchet start).

## R6. Standalone tool pinning (prek, zizmor, pip-audit)

- **Decision**: All three run as `uvx tool@X.Y.Z` at versions current at
  implementation time, pinned identically in justfile, prek config (zizmor
  hook), and CI. They are intentionally *not* project dependencies. zizmor
  runs with the regular persona.
- **Rationale**: Constitution mandates the uvx pattern; lodestar proves it.
  Single-source pinning in the justfile keeps local and CI in lockstep.
- **Alternatives considered**: Adding them to the dev dependency group —
  rejected: they are repo tools, not runtime/test code, and the constitution
  explicitly excludes them from project deps.

## R7. Dockerfile pattern

- **Decision**: Multi-stage build per the official `ghcr.io/astral-sh/uv`
  guidance: builder stage `uv sync --frozen --no-dev` into `/app/.venv`,
  runtime stage copies venv + source onto `python:3.14-slim`. A dev target
  layers the dev dependency group on the same base stages. Dev compose runs
  runserver with bind-mounted source; prod compose runs gunicorn with
  whitenoise, no mounts, restart policies. Dev applies migrations on start;
  prod documents migration as an explicit operator step.
- **Rationale**: Feature input settles this; shared stages guarantee the
  constitution's "dev and prod differ only by configuration".
- **Alternatives considered**: Separate dev/prod Dockerfiles — rejected
  (drift risk, violates shared-base-image rule); running migrations
  automatically in prod — rejected (operator action per feature input).

## R8. Tailwind standalone CLI

- **Decision**: Tailwind v4-series standalone binary, version pinned in the
  justfile. `tailwind-install` downloads the platform binary, verifies its
  SHA-256 against a checksum recorded in the justfile, and moves it into
  gitignored `bin/` (the htmx download-verify-move pattern).
  `just tailwind` rebuilds `static/css/tailwind.css` from
  `static/css/input.css`; the compiled output is committed. v4 CSS-first
  configuration (`@import "tailwindcss"` + `@source` directives in
  input.css) — no tailwind.config.js, no Node.
- **Rationale**: Constitution bans runtime CDNs and the feature bans the Node
  toolchain; committing the compiled sheet keeps fresh clones rendering with
  zero build steps.
- **Alternatives considered**: Node-based Tailwind — rejected (adds an entire
  toolchain for one binary's job); CDN script tag — constitutionally
  prohibited; django-tailwind package — rejected (wraps Node anyway).

## R9. htmx vendoring

- **Decision**: Latest htmx 2.x at implementation time, vendored at
  `static/js/htmx.min.js`. A justfile recipe (`htmx-update` or equivalent
  documented recipe) downloads a pinned version, verifies SHA-256, and moves
  it into place. Loaded from `base.html` via `{% static %}`.
- **Rationale**: Constitutional requirement (vendored, pinned,
  verified-download update recipe).
- **Alternatives considered**: unpkg/jsdelivr CDN — constitutionally
  prohibited; npm — no Node toolchain exists in this template.

## R10. Health check endpoint

- **Decision**: `GET /health/` wired in `config/urls.py` to
  `config/views.py:health_check`. Returns JSON; performs one trivial DB
  round-trip (`SELECT 1` via `django.db.connection`). 200 with
  `{"status": "ok", "database": "ok"}` when healthy; 503 with
  `{"status": "degraded", "database": "error"}` when the DB probe fails.
  Exempt from axes and unaffected by CSP (JSON response). Full contract in
  `contracts/health-endpoint.md`.
- **Rationale**: The permanent test surface (spec FR-002); deterministic
  behavior with the DB down was an explicit spec edge case, so both states
  are part of the contract.
- **Alternatives considered**: django-health-check package — rejected
  (Principle V: a view of ~15 lines needs no dependency); plain-text "OK" —
  rejected: JSON lets projects extend the payload without breaking
  consumers.

## R11. django-axes and django-csp defaults

- **Decision**: axes: enabled, 5 attempts, 1-hour cooloff, lockout by
  username+IP combination, comment pointing at what to tune per project.
  csp: django-csp 4.x style configuration, `default-src 'self'` baseline,
  no inline scripts (htmx is a static file, so none are needed), comments
  marking the directives projects most often need to extend. Both settings
  blocks carry "tune per project" comments.
- **Rationale**: Constitution requires both configured with safe defaults;
  conservative-but-working defaults keep the untouched scaffold green while
  establishing the hardening pattern.
- **Alternatives considered**: Shipping them installed but disabled —
  rejected: a disabled control is documentation, not hardening.

## R12. CI workflows and zizmor compliance

- **Decision**: Two workflows. `ci.yml`: one gate job running lint, format
  check, ty, coverage-gated pytest against a Postgres service container,
  pip-audit (fail-closed), deploy-check (`check --deploy --fail-level
  WARNING` with DEBUG=false against real settings), plus a zizmor job.
  `instantiation.yml`: checkout, run `scripts/instantiate.py testproject`,
  then the full gate suite against the result. All actions pinned by full
  commit SHA with trailing version comments; workflows declare least
  `permissions:`; `uv sync --frozen` everywhere so lockfile drift fails.
- **Rationale**: CI must mirror local gates (constitution) plus the
  suite-level gates; SHA pinning and explicit permissions are what zizmor's
  regular persona enforces.
- **Alternatives considered**: Single workflow with an instantiation job —
  rejected: `instantiation.yml` must be deletable by the script as one file
  without editing surviving CI; tag-pinned actions — fails zizmor.

## R13. Instantiation script design

- **Decision**: `scripts/instantiate.py`, stdlib only (argparse, pathlib, re,
  shutil, sys). Input: new project name, validated as a lowercase Python
  identifier (`str.isidentifier()`, not keyword, regex `[a-z_][a-z0-9_]*`)
  before any file is touched; invalid names exit non-zero with a clear
  message and zero modifications. Actions in one pass: rewrite
  `template_project` across pyproject metadata, compose service/image names,
  README, CLAUDE.md; remove `example/` and every reference (INSTALLED_APPS
  entry, urls include, coverage source entry, root references); delete
  itself and `.github/workflows/instantiation.yml`; print next steps.
  Re-run protection: if the `template_project` marker is absent, exit with a
  clear "already instantiated" message and no changes. Idempotence beyond
  that refusal is out of scope.
- **Rationale**: All settled by feature input (resolved decisions + technical
  context). Validation-before-mutation satisfies the spec's
  invalid-name/partial-rename edge cases.
- **Alternatives considered**: copier/cookiecutter — explicitly rejected in
  the spec's resolved decisions (repo must stay runnable as committed);
  shell script — rejected: stdlib Python is portable across the user's fish
  shell, sh, and CI.

## R14. Example-app isolation guard

- **Decision**: A check that greps for `example` imports (`from example`,
  `import example`) outside `example/` itself, failing if any exist. Runs in
  two places: inside `tests/test_instantiation.py` as a pre-condition, and
  as a step in `instantiation.yml`.
- **Rationale**: Plan-phase Constitution Check reminder from the feature
  input — the example app demonstrates layout and must never become
  load-bearing, or instantiation breaks the projects it creates.
- **Alternatives considered**: Import-linter dependency — rejected
  (Principle V: grep suffices for one rule).

## R15. Instantiation test strategy (local vs CI)

- **Decision**: `tests/test_instantiation.py` copies the repo to a temp
  directory, runs the script, and asserts structural post-conditions (no
  `template_project` outside allowed paths, no `example/` directory, no
  example references in settings/urls/pyproject, script and its workflow
  gone) — fast, deterministic, no Docker. The *full* gate suite on the
  instantiated result (uv sync, ruff, ty, pytest with coverage floor) runs
  in `instantiation.yml`, which has the environment for it.
- **Rationale**: Spec FR-023 requires automated coverage of instantiation;
  splitting structural assertions (local, every `just test`) from gate
  re-runs (CI, minutes-long) keeps the local suite fast and deterministic
  (Principle II) while CI proves the real thing.
- **Alternatives considered**: Running the full gate suite from inside a
  pytest test — rejected: nested uv/pytest invocations are slow, flaky, and
  break xdist determinism.
