# Contract: Health Check Endpoint

The permanent boot/verification surface for humans, tests, compose
healthchecks, and CI. Survives instantiation unchanged.

## Request

```
GET /health/
```

- No authentication, no CSRF, no session dependence.
- Exempt from django-axes throttling (it carries no credentials).
- Method: GET only; other methods receive 405.

## Responses

### Healthy — 200

```json
{"status": "ok", "database": "ok"}
```

Returned when one trivial database round-trip (`SELECT 1` via
`django.db.connection`) succeeds.

### Degraded — 503

```json
{"status": "degraded", "database": "error"}
```

Returned when the database probe raises. The response is deterministic: the
endpoint never hangs on the probe beyond the database driver's connect
timeout and never returns 500 for a down database — 503 is the contract.

## Guarantees

- Content-Type: `application/json` in both states.
- No side effects; safe to poll.
- Stateless: every request re-probes; no caching of health state.
- The integration test `tests/test_health.py` asserts the 200 path against
  a real database (no mocks, per Principle II). The 503 path is asserted by
  the same test module using a deliberately broken database alias/connection
  arranged through real objects, not by mocking the probe.

## Consumers

- `tests/test_health.py` (permanent integration test)
- Manual verification in the quickstart (`curl localhost:8000/health/`)
- Optional compose/orchestrator healthchecks in downstream projects
