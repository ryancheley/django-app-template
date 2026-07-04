<!--
Sync Impact Report
==================
Version change: (new) → 1.0.0
Rationale: Initial ratification of the constitution for the Django application
template. MAJOR version 1 establishes the baseline governance framework.

Modified principles: N/A (initial adoption)

Added sections:
- Core Principles (I. Code Quality, II. Testing Standards, III. Security by
  Default, IV. Accessibility, V. Simplicity and Reproducibility)
- Technology Stack
- Tooling and Automation Requirements
- Development Workflow
- Governance

Removed sections: N/A (initial adoption)

Templates requiring updates:
- ✅ .specify/templates/plan-template.md — Constitution Check gate is dynamic
  ("Gates determined based on constitution file"); Complexity Tracking table
  already matches the simpler-alternative-rejected requirement. No change
  needed.
- ✅ .specify/templates/spec-template.md — Success Criteria and Acceptance
  Scenarios sections are compatible; accessibility requirements enter at spec
  phase via Principle IV. No structural change needed.
- ✅ .specify/templates/tasks-template.md — Updated: "Tests are OPTIONAL" note
  replaced to align with Principle II (integration test per feature,
  regression test per bug fix are mandatory).
- ✅ .specify/templates/checklist-template.md — Generic checklist scaffold;
  no constitution-specific references. No change needed.

Follow-up TODOs: none
-->

# Django Application Template Constitution

This constitution governs a reusable Django application template: the starting
point for all new Django apps and sites. It is not tied to any single product
domain; every principle below is domain-agnostic and applies to any project
instantiated from this template.

## Core Principles

### I. Code Quality

Code is written for the next reader, not just the interpreter.

- All code MUST pass `ruff check` and `ruff format --check` before push. A
  failing linter is a blocking defect, not a warning.
- All Python code MUST pass type checking with `ty`. New code MUST be fully
  type-annotated. Any `# type: ignore` MUST carry an inline justification
  comment.
- ty's known Django false positives (`unresolved-attribute`,
  `invalid-assignment`, `invalid-argument-type`, `invalid-return-type`) MAY be
  downgraded project-wide with a comment explaining why, until ty gains Django
  awareness. All other rules stay at default severity.
- Functions and modules MUST have a single responsibility. Duplicated logic is
  extracted per the rule of three: tolerate two occurrences, extract on the
  third.
- Dead code, commented-out blocks, and unused dependencies MUST be removed in
  the change that orphans them.

**Rationale**: The template seeds many projects; quality debt introduced here
multiplies across every downstream instantiation.

### II. Testing Standards

- The test stack is pytest with pytest-django, pytest-xdist for parallel
  execution, and pytest-cov with an enforced coverage floor that ratchets
  upward and never downward.
- Test data comes from factory-boy. Tests exercise real objects. Mocks are
  permitted only at external service boundaries, and each mock MUST mirror a
  recorded or documented real response shape.
- Every feature MUST ship with at least one integration test covering its
  primary acceptance scenario. Every bug fix MUST include a regression test
  that fails before the fix.
- Tests MUST be deterministic: no wall-clock timing, no network dependence,
  no order dependence.
- The full suite MUST pass locally before any push and in CI before any merge.

**Rationale**: Real-object tests with a ratcheting coverage floor keep the
suite honest as projects diverge from the template; deterministic tests keep
CI trustworthy.

### III. Security by Default

- Secrets never enter the repository. gitleaks runs as a local hook and in CI.
  Configuration is supplied via environment variables with a committed
  `.env.example` and a gitignored `.env`.
- GitHub Actions workflows are audited with zizmor (pinned version, regular
  persona). Actions MUST be pinned. Workflow security findings block merge.
- Locked dependencies are scanned with pip-audit, failing closed on any
  advisory. Ignores MUST carry an inline reason and a review date.
- Django's deploy checks run against real production settings with DEBUG off
  (`manage.py check --deploy --fail-level WARNING`) as a standing gate, so
  SECURE_*/cookie/HSTS regressions fail fast.
- Baseline hardening ships with the template: django-axes for login
  throttling, django-csp for content security policy.

**Rationale**: Security controls baked into the template are inherited free by
every project; controls added later are frequently skipped under deadline
pressure.

### IV. Accessibility

- WCAG 2.1 Level AA is the minimum standard, AAA where feasible. Accessibility
  is blocking at spec, plan, and implementation phases. It is never deferred
  to post-launch polish.
- Semantic HTML is preferred over ARIA. Full keyboard operability with visible
  focus is REQUIRED. Color never conveys meaning alone. Contrast MUST meet
  4.5:1 for normal text and 3:1 for large text. Non-text content MUST have alt
  text or an aria-label. Labels and errors MUST be programmatically associated
  with form fields. `prefers-reduced-motion` MUST be respected.
- Third-party components MUST be vetted for accessibility before adoption.

**Rationale**: Retrofitting accessibility costs far more than building it in,
and a template that ships accessible defaults makes the accessible path the
default path.

### V. Simplicity and Reproducibility

- Django's built-in mechanisms (ORM, migrations, forms, auth, admin) are used
  before third-party packages. Every added dependency MUST be justified in the
  feature plan with the simpler rejected alternative recorded.
- A fresh clone MUST reach a running dev environment with `docker compose up`.
  No undocumented manual steps.
- Frontend assets are vendored; runtime CDNs are prohibited. htmx is pinned
  and vendored with a verified-download update recipe.

**Rationale**: Every dependency and manual step is a maintenance liability
replicated into every project the template spawns; boring, reproducible
defaults age best.

## Technology Stack

The stack is fixed. Deviations are constitutional amendments, not plan
decisions.

- **Python 3.14.** All code targets this version. No syntax or stdlib features
  beyond it.
- **Django** (current LTS or newer at template instantiation).
- **PostgreSQL** via psycopg. All schema changes go through Django migrations.
  Raw SQL requires justification and stays PostgreSQL-compatible.
- **uv** for all dependency and environment management. `uv.lock` is the
  single source of truth for tool versions. Linters and type checkers run
  through `uv run` so Dependabot bumps apply automatically with no pinned
  mirror revs to sync.
- **uvx for standalone tools.** prek, zizmor, and pip-audit run via pinned
  `uvx tool@version` invocations and are intentionally not project
  dependencies.
- **Docker and Docker Compose** for all services. Two compose files:
  `compose.yaml` for development and `compose.prod.yaml` for the reference
  production stack (gunicorn, whitenoise, DEBUG off). Dev and prod containers
  share base images and differ only by configuration.
- **Tailwind CSS** utility classes for all styling. Custom CSS only where
  Tailwind cannot achieve the result, confined to a single stylesheet entry
  point with an explanatory comment. No inline style attributes.
- **htmx** for frontend interactivity, vendored and pinned.

## Tooling and Automation Requirements

- **justfile** is the single entry point for all developer tasks. Required
  recipes at minimum: `up`, `down`, `migrate`, `test`, `test-fast` (reuse-db
  inner loop), `cov` (coverage-gated), `lint`, `typecheck`, `zizmor`, `audit`
  (pip-audit), `deploy-check`, `prek-install`, `prek`, and an aggregate
  `check` that chains lint, typecheck, zizmor, and cov. `just check` runs
  before every push.
- **prek** (Rust drop-in for pre-commit) runs the local hooks defined in
  `.pre-commit-config.yaml`: standard hygiene hooks (trailing whitespace,
  end-of-file, check-yaml, check-toml, large files, merge conflicts, private
  keys), gitleaks, ruff check with fix, ruff format, ty, and zizmor on
  workflow files. Local hooks mirror CI. CI remains the authoritative gate.
- **GitHub Actions CI** runs the same gates as the local hooks plus the
  coverage-gated test suite, dependency audit, and deploy check. CI checks are
  never bypassed.

## Development Workflow

- All work happens on feature branches. Direct pushes to main are prohibited
  without exception.
- Before any push: lint, format check, ty, and the full pytest suite pass
  locally via `just check`.
- Pull requests are squash-merged once green. After merge, switch back to main
  and pull.
- Commit messages start with an emoji and describe the change clearly.
- The `/speckit.plan` Constitution Check gate evaluates each feature plan
  against all principles and the Technology Stack section, recording justified
  violations in the plan's Complexity Tracking table.

## Governance

- This constitution supersedes all other practices. Amendments happen on a
  feature branch via pull request with the Sync Impact Report updated and
  dependent templates re-validated.
- Versioning follows semantic versioning: MAJOR for removed or redefined
  principles, MINOR for new principles or materially expanded guidance, PATCH
  for clarifications.
- Every PR review verifies compliance with this constitution. Violations block
  merge unless justified in the plan's Complexity Tracking table and accepted
  in review.
- Added complexity is always justified against a simpler rejected alternative.

**Version**: 1.0.0 | **Ratified**: 2026-07-04 | **Last Amended**: 2026-07-04
