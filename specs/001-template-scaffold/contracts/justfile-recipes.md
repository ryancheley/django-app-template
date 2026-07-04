# Contract: justfile Recipes

The justfile is the single developer-task entry point (constitution,
Tooling section). Every recipe below must exist and work against the
scaffold as shipped. Recipes are POSIX-sh portable: no fish syntax, no
bashisms.

## Constitutional recipes

| Recipe | Behavior |
|--------|----------|
| `up` | Start the dev compose stack (detached), db healthcheck gating web |
| `down` | Stop the dev stack |
| `migrate` | Run `manage.py migrate` in the web container |
| `test` | Full pytest suite, parallel (xdist), test settings |
| `test-fast` | Inner-loop pytest with `--reuse-db`, no coverage |
| `cov` | Test suite with coverage and the enforced `--cov-fail-under` floor |
| `lint` | `uv run ruff check` + `uv run ruff format --check` |
| `typecheck` | `uv run ty check` |
| `zizmor` | Pinned `uvx zizmor@X.Y.Z` over `.github/workflows/` |
| `audit` | Pinned `uvx pip-audit@X.Y.Z` against uv.lock export, fail-closed |
| `deploy-check` | `manage.py check --deploy --fail-level WARNING` with DEBUG=false and prod-shaped env |
| `prek-install` | Pinned `uvx prek@X.Y.Z install` |
| `prek` | Pinned `uvx prek@X.Y.Z run --all-files` |
| `check` | Aggregate: lint → typecheck → zizmor → cov (the pre-push gate) |

## Template-specific recipes

| Recipe | Behavior |
|--------|----------|
| `tailwind-install` | Download the pinned standalone Tailwind CLI for the current platform, verify SHA-256 against the checksum recorded in the justfile, move into gitignored `bin/` |
| `tailwind` | Rebuild `static/css/tailwind.css` from `static/css/input.css` with the installed CLI (minified) |
| `htmx-update` | Download the pinned htmx version, verify SHA-256, move to `static/js/htmx.min.js` |

## Cross-cutting guarantees

- Tool versions for uvx-run tools (prek, zizmor, pip-audit, Tailwind CLI,
  htmx) are pinned once at the top of the justfile as variables; the prek
  config and CI reference the same versions.
- Host-side database recipes assume Postgres on host port 5433 (dev compose
  mapping).
- `just check` is the mandatory pre-push gate; CLAUDE.md and README state
  this.
- Recipes that need env vars read `.env` via compose or explicit exports —
  no recipe requires fish- or bash-specific behavior.
