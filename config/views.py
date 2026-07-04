"""Permanent views living in the config package (never in the example app,
which is deleted at instantiation)."""

from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health_check(request: HttpRequest) -> JsonResponse:
    """Boot/liveness signal: 200 when the database answers, 503 when it
    does not. Contract: specs/001-template-scaffold/contracts/health-endpoint.md.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "degraded", "database": "error"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})
