# Testing

Backend tests cover deterministic JSON validation, actionable errors, idempotency conflict behavior, tenant isolation, webhook signing, and bounded retry backoff. Frontend tests cover the seeded authentication surface. CI runs lint, type checks, unit tests, production build, Compose validation, and secret scanning. `make test` and `make lint` are the local gates.

