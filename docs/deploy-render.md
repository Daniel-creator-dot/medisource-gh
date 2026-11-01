# Deploy MediSource GH on Render

This is a free demonstration deploy, not a production launch. Render's free Postgres database expires 30 days after creation. Free web services sleep after 15 minutes without a request and take about a minute to wake. The first page load after a sleep can fail while the API is still starting; refresh once.

Regulatory approvals, live payments, and real clinician listings are still not part of this build. The seeded suppliers and products are fictional.

## What gets created

`render.yaml` defines three free resources:

| Resource | Name | Role |
| --- | --- | --- |
| Web service | `medisource-gh-web` | Next.js site |
| Web service | `medisource-gh-api` | Django API |
| Postgres | `medisource-gh-db` | Database |

Redis is not included. The API runs without it. Celery has no worker on this deploy, and nothing in the current release sends a background task during a request.

Each API start migrates the database and loads the labelled sample catalogue. Render's free plan does not run a separate release command. Sample accounts use the password `Demo-Only-Change-Me-1`.

- `ada.customer@sample.medisource.test`
- `kofi.supplier@sample.medisource.test`
- `ama.supplier@sample.medisource.test`
- `yaw.admin@sample.medisource.test`

The sample admin is a privileged account. Production settings require an authenticator before that account receives a session. The customer account can sign in without one.

Public site: `https://medisource-gh-web.onrender.com`

API docs: `https://medisource-gh-api.onrender.com/api/docs/`

If either name is already taken on Render, rename both services in `render.yaml` and update `WEB_ORIGIN`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, and `NEXT_PUBLIC_API_URL` so the browser origin and the API origin still match.

## Deploy

1. Push this repository to GitHub.
2. In the [Render dashboard](https://dashboard.render.com), choose **New** → **Blueprint**.
3. Select the repository. Render reads `render.yaml`.
4. Apply the blueprint. No credit card is required for the free plans.
5. Open the web service URL after both deploys are live. If the catalogue message says the API is sleeping, wait a minute and refresh.

Turn `FORCE_SEED_DEMO` off before any real supplier or customer data is stored. The seed command updates the fictional rows; it should not run against a live catalogue.

## Email

The host uses Django's console email backend. Verification and password-reset messages are written to the API logs, not delivered to an inbox. Add SMTP environment variables before relying on those emails.

## Local run

PostgreSQL and Redis:

```powershell
docker compose up -d
```

Copy `.env.example` to `.env`, then from `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

From the repository root, with Node 24:

```powershell
npm install
npm run dev
```

The site is at `http://localhost:3000` and the API at `http://localhost:8000`. If Docker is not installed, local settings fall back to a SQLite file when `DATABASE_URL` is empty. Tests use SQLite unless `USE_POSTGRES_TESTS=true`.

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```
