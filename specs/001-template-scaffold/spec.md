# Feature Specification: Django Application Template Scaffold

**Feature Branch**: `001-template-scaffold`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Build the initial scaffold of a reusable Django application template repository. The template is what Claude Code clones or copies as the starting point for every new Django app or site I build. The deliverable of this feature is the template repo itself: a fresh clone must reach a running, fully gated Django project with a single command, and every quality gate defined in the constitution must pass on the untouched scaffold."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fresh Start (Priority: P1)

A developer instantiates the template, runs one bootstrap command, and gets a
running development site at localhost with a database, migrations applied, and
a health check responding. No manual wiring of linters, hooks, CI, or
containers is required.

**Why this priority**: This is the template's reason to exist. If a fresh
clone does not reach a running site with one command, nothing else about the
template matters.

**Independent Test**: Clone the repository into an empty directory, copy
`.env.example` to `.env`, run the single bootstrap command, and request the
health check endpoint. Delivers a verifiably running project with zero
undocumented steps.

**Acceptance Scenarios**:

1. **Given** a fresh clone and a copied `.env` file, **When** the developer
   runs the single bootstrap command, **Then** the dev site responds at
   localhost with migrations applied and the health check returning success.
2. **Given** a warm Docker cache, **When** the developer performs the full
   clone-to-running-site path, **Then** elapsed time is under five minutes.
3. **Given** the dev stack is running, **When** the developer inspects service
   logs, **Then** no errors appear.

---

### User Story 2 - All Gates Green on the Untouched Scaffold (Priority: P2)

A developer makes a trivial change, commits, and pushes to a new GitHub
repository. Local hooks pass on commit, the aggregate local gate passes before
push, and CI runs the full gate suite green on the first push with no
repository configuration beyond creating the repo.

**Why this priority**: The template's promise is "fully gated from day one."
A scaffold that ships with failing or skipped gates trains users to bypass
them, which violates the constitution's core premise.

**Independent Test**: On an untouched clone, run the local hook suite over all
files, run the aggregate check command, then push to a new GitHub repository
and observe the CI run. All three must pass without modifying any shipped
file.

**Acceptance Scenarios**:

1. **Given** an untouched scaffold, **When** the local hook suite runs over
   all files, **Then** every hook passes (hygiene, secret scanning, lint,
   format, type check, workflow audit).
2. **Given** an untouched scaffold, **When** the aggregate local check runs,
   **Then** lint, type check, workflow audit, and the coverage-gated test
   suite all pass.
3. **Given** a new GitHub repository with default settings and no secrets
   configured, **When** the scaffold is pushed for the first time, **Then**
   CI completes green across the full gate suite (lint, type check, workflow
   audit, coverage-gated tests, dependency audit, deploy check).
4. **Given** the shipped scaffold, **When** any file is inspected, **Then** no
   TODO, FIXME, or placeholder exists that fails a gate; placeholders that
   require user action (project name, license holder) are documented in the
   README and do not fail any gate.

---

### User Story 3 - Instantiation (Priority: P3)

A developer creates a new project from the template, runs the single
instantiation script with the new project name, and receives a consistently
renamed project with the example app fully removed. All gates remain green and
the site still boots with the health check responding.

**Why this priority**: Instantiation is the bridge from template to real
project. It depends on Stories 1 and 2 existing, but a broken rename or
half-removed example app would poison every project created from the
template.

**Independent Test**: Run the instantiation script against a copy of the
repository with a new name, then run the full local gate suite and boot the
dev stack. Delivers a renamed, example-free project with everything still
green.

**Acceptance Scenarios**:

1. **Given** a fresh copy of the template, **When** the instantiation script
   runs with a new project name, **Then** the project name is applied
   consistently across the project package, container service names, and
   project metadata in one pass.
2. **Given** the instantiation script has run, **When** the example app is
   searched for, **Then** no trace remains: source, URL wiring, templates,
   tests, coverage source entry, and installed-apps entry are all gone.
3. **Given** an instantiated project, **When** the aggregate local check and
   the full local hook suite run, **Then** both pass, including the coverage
   floor.
4. **Given** an instantiated project, **When** the dev stack is started,
   **Then** the site boots and the health check responds.
5. **Given** the template repository's own CI, **When** the test suite runs,
   **Then** an automated test or CI job executes the instantiation script
   against a copy of the repository and asserts the gates pass afterward, so
   instantiation can never silently rot.

---

### User Story 4 - Agent and Speckit Readiness (Priority: P4)

Claude Code, operating inside a project created from the template, discovers
how to run, test, and gate its own work from the repository's own context
files without being told. The developer runs the Speckit chain immediately:
the constitution is already ratified and the plan-phase Constitution Check
evaluates against it with no setup.

**Why this priority**: This makes the template self-describing for agent-led
development, but it builds on the scaffold, gates, and instantiation being in
place first.

**Independent Test**: In a fresh clone, verify the agent context file
accurately describes the layout, task recipes, and gate expectations, and
verify the Speckit chain's planning phase can read the committed constitution
without any prior setup step.

**Acceptance Scenarios**:

1. **Given** a fresh clone, **When** an agent reads the repository's context
   file, **Then** it can determine the project layout, every developer task
   recipe, the gate expectations, and the rule that the aggregate check runs
   before every push.
2. **Given** a fresh clone, **When** the Speckit planning phase runs its
   Constitution Check, **Then** the ratified constitution and all Speckit
   template and command files are present and usable with no setup.

---

### Edge Cases

- What happens when the instantiation script is run twice, or run with the
  name the project already has? It must fail clearly or complete as a no-op
  without corrupting files — never a partial rename.
- What happens when the instantiation script is given an invalid project name
  (spaces, leading digit, reserved word, uppercase mixed with hyphens)? It
  must reject the name with a clear message before touching any file.
- What happens when a fresh clone starts the dev stack without copying
  `.env.example` to `.env`? The failure must be immediate and the required
  step documented in the README, not a silent misconfiguration.
- What happens to the coverage floor when the example app (and its tests) is
  removed? The floor must hold in both states: untouched scaffold and
  post-instantiation.
- What happens when the health check is requested while the database is
  unavailable? The endpoint's behavior must be deterministic and documented
  (it is the signal used to verify a successful boot).
- What happens on a cold Docker cache? The five-minute target applies to a
  warm cache; a cold start must still complete without errors, just slower.

## Requirements *(mandatory)*

### Functional Requirements

#### Scaffold contents

- **FR-001**: The template MUST contain a minimal but real Django project: a
  config package with settings that switch dev/test/prod behavior via
  environment variables, one example app demonstrating the expected layout
  (models, views, urls, templates, tests), a base page template with the
  vendored interactivity library and compiled stylesheet wired in, and a
  health check endpoint.
- **FR-002**: The health check and every other permanent surface MUST live in
  the config package or a permanent core app, never in the example app. The
  example app exists purely as living documentation of the expected app
  layout and is deleted at instantiation; nothing permanent may depend on it.
- **FR-003**: The template MUST ship a working test suite with enough real
  tests to make the coverage floor meaningful on day one, including at
  minimum: one integration test hitting the health check (permanent, survives
  instantiation) and one model test using the test-data factory chain in the
  example app (deleted at instantiation).
- **FR-004**: The compiled stylesheet MUST be committed so a fresh clone
  renders correctly without a build step, and a task recipe MUST rebuild it
  using the pinned standalone CLI binary with a download-and-verify recipe.
  No Node toolchain may be required.
- **FR-005**: The template MUST provide a development container stack and a
  reference production container stack (production server, static file
  serving, debug off) that share base images and differ only by
  configuration, with PostgreSQL in both.
- **FR-006**: A committed `.env.example` MUST document every environment
  variable either container stack reads; the real `.env` is gitignored.
- **FR-007**: The template MUST include the complete task-runner file with all
  recipes required by the constitution (`up`, `down`, `migrate`, `test`,
  `test-fast`, `cov`, `lint`, `typecheck`, `zizmor`, `audit`, `deploy-check`,
  `prek-install`, `prek`, `tailwind`, and the aggregate `check`), all
  functional against the scaffold as shipped.
- **FR-008**: The template MUST include the local hook configuration with the
  full hook set from the constitution: hygiene hooks (trailing whitespace,
  end-of-file, YAML/TOML checks, large files, merge conflicts, private keys),
  secret scanning, lint with fix, format, type check, and workflow audit on
  workflow files.
- **FR-009**: The template MUST include CI workflows that run the same gates
  as the local hooks plus the coverage-gated test suite, dependency audit,
  and deploy check. All workflow actions MUST be pinned by commit SHA, and
  the workflows themselves MUST pass the workflow auditor at its pinned
  version.
- **FR-010**: The template MUST include project metadata and tool
  configuration managed by the standard dependency manager: Python 3.14,
  linter and type checker configured per the constitution (including the
  documented type-checker Django false-positive downgrades with an
  explanatory comment), and coverage configuration with the floor set to the
  scaffold's actual measured coverage.
- **FR-011**: The template MUST include repository hygiene files: ignore files
  for git and containers, a secret-scanner configuration with an empty
  allowlist (present so the pattern is established), a license placeholder,
  and a README explaining the five-minute path from clone to running site,
  including every placeholder that requires user action.
- **FR-012**: The template MUST include an agent context file describing the
  project layout, the task recipes, the gate expectations, and the rule that
  the aggregate check runs before every push.
- **FR-013**: The template MUST include the ratified constitution and the
  Speckit template and command files so the specify/plan/tasks/implement
  chain works out of the box, with the plan-phase Constitution Check able to
  evaluate against the committed constitution without setup.
- **FR-014**: Login throttling and content security policy protections MUST
  ship configured with safe defaults. No custom authentication flows beyond
  the framework's defaults.

#### Gates on the untouched scaffold

- **FR-015**: The aggregate local check MUST pass on the untouched scaffold as
  shipped.
- **FR-016**: The full local hook suite MUST pass over all files on the
  untouched scaffold as shipped.
- **FR-017**: CI MUST be green on the first push to a new repository with no
  configuration beyond repo creation (no secrets, no settings changes).
- **FR-018**: No shipped file may contain a TODO, FIXME, or placeholder that
  fails a gate. Placeholders requiring user action MUST be documented in the
  README and MUST NOT fail any gate.

#### Instantiation

- **FR-019**: A single instantiation script MUST rename the project
  consistently across the project package, container service names, and
  project metadata in one pass. It MUST be written in stdlib-only Python so
  it runs before any environment setup. No templating syntax may appear in
  the repository; the repo stays runnable and gate-testable exactly as
  committed.
- **FR-020**: The same script MUST remove the example app completely in the
  same pass: source, URL wiring, templates, tests, coverage source entry, and
  installed-apps entry.
- **FR-021**: After the script runs, the aggregate local check and the full
  local hook suite MUST both pass, the coverage floor MUST still hold, and
  the dev site MUST boot with the health check responding.
- **FR-022**: The instantiation script MUST validate the requested project
  name before modifying any file and MUST reject invalid names with a clear
  message, leaving the repository untouched.
- **FR-023**: The instantiation script MUST itself be exercised by an
  automated test or CI job that runs it against a copy of the repository and
  asserts the gates pass afterward.

### Out of Scope

- Any product or domain functionality beyond the example app and health
  check.
- Authentication flows beyond the framework's defaults (no LDAP, no SSO).
- Deployment automation to any specific host (no Coolify, Hetzner, or
  Kubernetes manifests). The production container stack is a reference, not a
  deploy pipeline.
- Documentation site tooling. Per-project decision.
- Background-worker or workflow-orchestration patterns. Add per project when
  needed.
- Multi-tenancy, internationalization, and API frameworks. Per-project
  decisions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A fresh clone reaches a responding dev site with zero errors in
  service logs using a single bootstrap command, in under five minutes on a
  warm container cache.
- **SC-002**: The aggregate local check passes on the untouched scaffold with
  zero failures.
- **SC-003**: The full local hook suite passes over all files on the untouched
  scaffold with zero failures.
- **SC-004**: CI is green on the first push to a new repository with zero
  configuration steps beyond creating the repository.
- **SC-005**: After instantiation with a new project name, zero references to
  the placeholder name or the example app remain, all local gates pass, the
  coverage floor holds, and the site boots with the health check responding.
- **SC-006**: The instantiation path is covered by an automated test or CI
  job, so a change that breaks instantiation is caught before merge, not by
  the next person instantiating the template.
- **SC-007**: A search of shipped files finds zero TODO or FIXME markers and
  zero placeholders that fail a gate; every user-action placeholder is listed
  in the README.

## Assumptions

- The single bootstrap command is the container-stack start command (plus the
  documented one-time copy of `.env.example` to `.env`); "no undocumented
  manual steps" permits documented ones.
- The five-minute clone-to-running-site target assumes a warm container
  cache and a typical broadband connection; cold-cache first runs may take
  longer but must still succeed.
- CI runs on GitHub-hosted default runners; "zero configuration beyond repo
  creation" means no repository secrets, environments, or settings changes
  are needed for the gate suite to pass.
- The coverage floor is set from the scaffold's actual measured coverage at
  ship time, and the permanent tests (health check integration test and any
  core-app tests) are sufficient to hold that floor after the example app and
  its tests are removed together.
- The health check endpoint is the agreed signal of a successful boot for
  humans, scripts, and CI alike; its exact response contract is a planning
  decision.
- "Placeholder project name" means a real, valid, working name the template
  runs under as committed — not templating syntax — per the resolved
  instantiation decision.
- The template targets exactly one instantiation mechanism: copy or GitHub
  template repo followed by the instantiation script. Downstream projects may
  diverge afterward without constraint from this feature.
