"""ASGI entry point."""

import os

from django.core.handlers.asgi import ASGIHandler
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application: ASGIHandler = get_asgi_application()
