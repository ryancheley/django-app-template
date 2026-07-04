# Multi-stage build following the official astral-sh/uv pattern.
# Dev and prod share these stages and differ only by configuration
# (constitution: Technology Stack).

# --- builder: resolve locked runtime dependencies into /app/.venv ----------
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev
COPY . /app

# --- dev: adds the dev dependency group; used by compose.yaml --------------
FROM builder AS dev
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# --- runtime: slim production image; used by compose.prod.yaml -------------
FROM python:3.14-slim-trixie AS runtime
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /app /app
# Build the whitenoise manifest at image build time; the dummy SECRET_KEY is
# never used at runtime and collectstatic touches no database.
RUN DEBUG=false SECRET_KEY=collectstatic-build-only python manage.py collectstatic --noinput
RUN useradd --create-home appuser && chown -R appuser:appuser /app/staticfiles
USER appuser
EXPOSE 8000
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]
