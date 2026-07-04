"""WSGI entry point. Used by gunicorn in the production compose stack."""

import os

from django.core.handlers.wsgi import WSGIHandler
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application: WSGIHandler = get_wsgi_application()
