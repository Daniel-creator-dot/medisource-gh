# Infrastructure

`docker-compose.yml` at the repository root starts PostgreSQL 16, Redis 7, and the Django API for local development. It is not a production deployment. The database password and Django secret in that file are development defaults.

The Next.js app is intended to run on the host during development so the browser can reach `http://localhost:8000`. `infrastructure/docker/web.Dockerfile` builds the public site when you want it in a container. Pass `API_URL_INTERNAL=http://backend:8000` at runtime for server-side fetches inside Compose, and keep `NEXT_PUBLIC_API_URL` pointed at an address the browser can reach.

## Backups

Take a logical backup with `pg_dump` before any production upgrade. This milestone does not schedule backups. A restore drill should exist before real accounts or payments are stored.

```bash
docker compose exec postgres pg_dump -U medisource medisource > medisource.sql
```

## Continuous integration

`.github/workflows/ci.yml` runs the Django suite against PostgreSQL and typechecks the web app. The local default remains SQLite unless `USE_POSTGRES_TESTS=true`.
