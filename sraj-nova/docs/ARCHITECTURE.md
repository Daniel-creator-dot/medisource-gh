# Architecture

The system is a modular monolith.

- `backend/modules/identity` — users, roles, cookies, authenticator enrollment.
- `backend/modules/organization` — agency, clients, sites, contracts, command center.
- `backend/modules/workforce` — employees, identifiers, legal employer, deployments.
- `backend/modules/operations` — shifts, attendance events, adjustments, staffing requests, alerts.
- `backend/modules/governance` — audit rows and a transactional outbox.

The Next.js app in `apps/command-web` proxies `/api` to Django so the session cookie stays on the web origin. API paths are normalized with a trailing slash before Django routing, because the proxy does not preserve it. Operational metrics are aggregated in `operations/services.py`. Financial fields are returned as null with `payroll_engine` and `billing_engine` set to `not_active`.

An outbox row is written in the same database transaction as an audit event. No Celery worker publishes those rows in this milestone. Redis and PostgreSQL are defined in Docker Compose. Local runs without Docker use SQLite.

Kubernetes, Kafka, and a separate AI service are not used.
