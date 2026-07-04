"""Django settings for template_project.

Single env-driven settings module (no base/dev/prod split): dev/prod parity
is enforced through environment variables, and the deploy-check gate runs
THIS module with DEBUG=false. Defaults below are safe for development only.
"""

import os
from pathlib import Path

from csp.constants import SELF


def env_bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = Path(__file__).resolve().parent.parent

# Dev-only fallback; production supplies SECRET_KEY via the environment and
# the deploy check fails on this weak default.
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-only")

DEBUG = env_bool("DEBUG", default=True)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Baseline hardening (constitution: Security by Default)
    "axes",
    # Apps
    "example",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Whitenoise serves collected static files in production (no separate
    # static file server in the reference stack).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    # AxesMiddleware must come after auth middleware.
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# PostgreSQL only (constitution: Technology Stack). Defaults suit host-side
# development against the compose db, which maps host port 5433 -> 5432 to
# avoid colliding with a locally installed Postgres on 5432. Inside compose,
# the environment overrides HOST/PORT to db:5432.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "template_project"),
        "USER": os.environ.get("POSTGRES_USER", "template_project"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "dev-only-password"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5433"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{n}"}
    for n in (
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    )
]

# django-axes must be first so lockouts are checked before normal auth.
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # Hashed + compressed static files in production; plain storage in
        # DEBUG so dev and tests need no collectstatic step.
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Security hardening -----------------------------------------------------
# All of these harden automatically when DEBUG is false so that
# `manage.py check --deploy --fail-level WARNING` passes with prod-shaped env
# and regressions fail fast (constitution: Security by Default).

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", default=not DEBUG)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# django-axes: login throttling. Tune per project — these are conservative
# starting values, not a policy statement.
AXES_FAILURE_LIMIT = 5  # lockout after 5 failed attempts
AXES_COOLOFF_TIME = 1  # hours until a lockout expires
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]  # lock the pair, not all users on an IP

# django-csp: strict baseline — same-origin everything, no inline scripts.
# htmx and the compiled Tailwind stylesheet are same-origin static files, so
# this works as-is. Projects typically extend img-src/connect-src first.
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [SELF],
        "script-src": [SELF],
        "style-src": [SELF],
        "img-src": [SELF, "data:"],
        "base-uri": [SELF],
        "form-action": [SELF],
        "frame-ancestors": [SELF],
    }
}
