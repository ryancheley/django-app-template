"""pytest settings: import the real settings, override only what tests need.

Kept separate so the deploy-check gate exercises config.settings untouched.
"""

from config.settings import *  # noqa: F403

# Host-side test runs reach the compose db through the host port mapping
# 5433 -> 5432 (chosen so a locally installed Postgres on 5432 never
# collides). CI overrides via POSTGRES_HOST/POSTGRES_PORT env instead.
import os

DATABASES["default"]["HOST"] = os.environ.get("POSTGRES_HOST", "localhost")  # noqa: F405
DATABASES["default"]["PORT"] = os.environ.get("POSTGRES_PORT", "5433")  # noqa: F405

# Fast, deterministic tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Plain static storage: tests must not require a collectstatic step
# (manifest storage raises on unhashed references).
STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.StaticFilesStorage"  # noqa: F405

# Axes interferes with test-client logins; its own behavior is not under test
# in the template. Projects testing lockout flows re-enable it per-test.
AXES_ENABLED = False
