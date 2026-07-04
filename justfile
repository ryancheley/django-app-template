# Single entry point for developer tasks (constitution: Tooling).
# `just check` runs before every push. Recipes are POSIX-sh portable: no
# fish syntax, no bashisms.

# Standalone tools run via pinned uvx and are intentionally not project
# dependencies; ruff/ty run through `uv run` so uv.lock pins them.
PREK_VERSION := "0.4.8"
ZIZMOR_VERSION := "1.26.1"
PIP_AUDIT_VERSION := "2.10.1"

# Tailwind standalone CLI (no Node toolchain) and vendored htmx, both
# download-verify-move with checksums recorded here.
TAILWIND_VERSION := "4.3.2"
TAILWIND_SHA256_MACOS_ARM64 := "b800b0659dc64b9f03ede5660244d9415d777d5739ae2889280877ca37be742a"
TAILWIND_SHA256_LINUX_X64 := "5036c4fb4328e0bcdbb6065c70d8ac9452e0d4c947113a788a8f94fd390425c1"
HTMX_VERSION := "2.0.9"
HTMX_SHA256 := "57d9191515339922bd1356d7b2d80b1ee3b29f1b3a2c65a078bb8b2e8fd9ae5f"

# Start the dev compose stack (db healthcheck gates web)
up:
    docker compose up -d --wait

# Stop the dev compose stack
down:
    docker compose down

# Apply migrations inside the web container
migrate:
    docker compose run --rm web python manage.py migrate

# Full test suite (xdist parallel via pyproject addopts)
test:
    uv run pytest

# Inner-loop tests: reuse the test database between runs
test-fast:
    uv run pytest --reuse-db

# Coverage-gated test suite; floor lives in pyproject [tool.coverage.report]
# (mirrors the CI test job)
cov:
    uv run pytest --cov

# ruff lint + format check (mirrors the CI lint job)
lint:
    uv run ruff check .
    uv run ruff format --check .

# ty type check; --exit-zero-on-warning because the four documented Django
# false positives are downgraded to warn in pyproject (mirrors CI typecheck)
typecheck:
    uv run ty check --exit-zero-on-warning

# Audit GitHub Actions workflows, regular persona (mirrors CI zizmor job)
zizmor:
    uvx zizmor@{{ZIZMOR_VERSION}} --persona regular .github/workflows/

# Audit locked dependencies, failing closed on any advisory (mirrors CI)
audit:
    #!/usr/bin/env sh
    set -eu
    tmp=$(mktemp)
    uv export --frozen --quiet --no-emit-project -o "$tmp"
    uvx pip-audit@{{PIP_AUDIT_VERSION}} --disable-pip -r "$tmp"
    rm -f "$tmp"

# Django deploy checks against the REAL settings module with DEBUG off;
# the throwaway SECRET_KEY only satisfies the strength check (mirrors CI)
deploy-check:
    #!/usr/bin/env sh
    set -eu
    SECRET_KEY=$(uv run python -c "import secrets; print(secrets.token_urlsafe(64))") \
    DEBUG=false \
    ALLOWED_HOSTS=example.com \
    uv run python manage.py check --deploy --fail-level WARNING

# Install the prek git hooks
prek-install:
    uvx prek@{{PREK_VERSION}} install

# Run every prek hook over every file
prek:
    uvx prek@{{PREK_VERSION}} run --all-files

# Download the pinned Tailwind standalone CLI, verify its checksum, and
# install it into gitignored bin/
tailwind-install:
    #!/usr/bin/env sh
    set -eu
    case "$(uname -s)-$(uname -m)" in
        Darwin-arm64) asset="tailwindcss-macos-arm64"; sum="{{TAILWIND_SHA256_MACOS_ARM64}}" ;;
        Linux-x86_64) asset="tailwindcss-linux-x64"; sum="{{TAILWIND_SHA256_LINUX_X64}}" ;;
        *) echo "Unsupported platform $(uname -s)-$(uname -m): add its checksum to the justfile" >&2; exit 1 ;;
    esac
    mkdir -p bin
    curl -fsSL -o bin/tailwindcss.tmp "https://github.com/tailwindlabs/tailwindcss/releases/download/v{{TAILWIND_VERSION}}/$asset"
    if command -v sha256sum >/dev/null 2>&1; then
        echo "$sum  bin/tailwindcss.tmp" | sha256sum -c -
    else
        echo "$sum  bin/tailwindcss.tmp" | shasum -a 256 -c -
    fi
    mv bin/tailwindcss.tmp bin/tailwindcss
    chmod +x bin/tailwindcss

# Rebuild the committed stylesheet from static/css/input.css
tailwind:
    ./bin/tailwindcss -i static/css/input.css -o static/css/tailwind.css --minify

# Download the pinned htmx, verify its checksum, and vendor it
htmx-update:
    #!/usr/bin/env sh
    set -eu
    curl -fsSL -o static/js/htmx.min.js.tmp "https://github.com/bigskysoftware/htmx/releases/download/v{{HTMX_VERSION}}/htmx.min.js"
    if command -v sha256sum >/dev/null 2>&1; then
        echo "{{HTMX_SHA256}}  static/js/htmx.min.js.tmp" | sha256sum -c -
    else
        echo "{{HTMX_SHA256}}  static/js/htmx.min.js.tmp" | shasum -a 256 -c -
    fi
    mv static/js/htmx.min.js.tmp static/js/htmx.min.js

# Aggregate pre-push gate: lint -> typecheck -> zizmor -> cov
check: lint typecheck zizmor cov
