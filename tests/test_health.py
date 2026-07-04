"""Integration tests for the permanent health check surface.

Contract: specs/001-template-scaffold/contracts/health-endpoint.md.
No mocks: the healthy path talks to the real test database, and the degraded
path breaks the real connection by pointing it at a port nothing listens on.
"""

import pytest
from django.db import connection
from django.test import Client


@pytest.mark.django_db
def test_health_returns_ok_when_database_reachable(client: Client) -> None:
    response = client.get("/health/")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert response.json() == {"status": "ok", "database": "ok"}


@pytest.mark.django_db
def test_health_rejects_non_get(client: Client) -> None:
    assert client.post("/health/").status_code == 405


@pytest.mark.django_db(transaction=True)
def test_health_returns_503_when_database_unreachable(client: Client) -> None:
    connection.close()
    original_port = connection.settings_dict["PORT"]
    # Port 9 (discard) refuses immediately: deterministic failure, no timeout.
    connection.settings_dict["PORT"] = "9"
    try:
        response = client.get("/health/")
    finally:
        connection.close()
        connection.settings_dict["PORT"] = original_port
    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "error"}
