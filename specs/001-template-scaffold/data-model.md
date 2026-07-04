# Data Model: Django Application Template Scaffold

The scaffold intentionally carries almost no domain data. Two "entities"
matter: the example model (disposable, exists to demonstrate conventions)
and the health check payload (permanent, a response shape rather than stored
data).

## ExampleItem (example app — removed at instantiation)

Demonstrates the expected conventions: typed fields, `__str__`, ordering,
timestamps, a factory, admin registration, and an app-local test.

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | auto primary key | — | Django default |
| name | CharField(200) | required, non-blank | demonstrates a validated text field |
| notes | TextField | blank allowed, default "" | demonstrates optional text without NULL |
| created_at | DateTimeField | auto_now_add | demonstrates timestamp convention |
| updated_at | DateTimeField | auto_now | demonstrates timestamp convention |

- **Ordering**: `-created_at` (newest first) via `Meta.ordering`.
- **String representation**: `name`.
- **Factory**: `example/factories.py` — `ExampleItemFactory` with a
  `Sequence`-based unique name (deterministic — no random/faker time
  dependence, per Principle II).
- **Admin**: registered with `list_display = ("name", "created_at")`.
- **Migration**: exactly one (`0001_initial`), deleted with the app at
  instantiation.
- **Validation rules**: framework-level only (max_length, blank/non-blank).
  No custom validators — the model demonstrates layout, not business logic.
- **Isolation invariant**: nothing outside `example/` may import from it
  (enforced by the R14 grep guard).

## Health check payload (config — permanent)

Not a stored entity; a response contract (full detail in
`contracts/health-endpoint.md`).

| Key | Type | Values |
|-----|------|--------|
| status | string | `"ok"` \| `"degraded"` |
| database | string | `"ok"` \| `"error"` |

State transitions: stateless — each request re-probes the database with one
trivial round-trip; there is no cached or persisted health state.

## Entities that do NOT exist (by design)

- No custom user model ships. Adding one is the first decision a real
  project makes, and Django requires it before the first migration — the
  README documents this as the recommended first post-instantiation step.
  The template itself has no users beyond Django's defaults.
- No site/tenant/config models — out of scope per spec.
