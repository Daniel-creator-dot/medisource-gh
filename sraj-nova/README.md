# SRAJ NOVA Workforce ERP

SRAJ NOVA is the workforce agency. Client factories are external organizations.

Milestone 1 provides agency configuration, sign-in, role-scoped access, and a command center whose operational counts come from stored records. Payroll, payments, and invoices are not calculated.

## Run locally

From `sraj-nova/backend`, with `DJANGO_SETTINGS_MODULE` unset:

```
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py seed_demo
.\.venv\Scripts\python manage.py runserver 127.0.0.1:8010
```

From `sraj-nova/apps/command-web`:

```
npm install
npm run dev
```

Open http://localhost:3010. Demonstration password: `Demo-Only-Change-Me-1`.

The same demonstration is deployed on the existing Render services:

- https://medisource-gh-web.onrender.com
- https://medisource-gh-api.onrender.com

Those hostnames are unchanged so the free Render workspace does not gain extra services. The site they serve is SRAJ NOVA, one agency with sample client organizations.

- `nova.owner@sample.sraj.test` — agency owner
- `nova.ops@sample.sraj.test` — operations
- `client.ashanti@sample.sraj.test` — one client only
- `worker.ama@sample.sraj.test` — one employee record

`python -m pytest` from the backend runs the access tests. Docker Compose is provided for PostgreSQL 16 and Redis. This machine does not have Docker, so local development uses SQLite.

## What is not in this milestone

Weekly payroll, statutory calculations, salary payments, client invoices, recruitment workflows, and the AI assistant are later milestones. The command center states that those engines are not active.
