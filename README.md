# MediSource GH

Healthcare marketplace for Ghana. This repository is the first working slice: a Django API, a Next.js public site and customer account, and a labelled sample catalogue. It is not a live pharmacy, clinic, or payment service.

The sample suppliers and products are fictional. Checkout is disabled for them. Pharmaceutical checkout stays closed. No clinicians are listed.

## What works now

- Customer registration, sign-in, email verification tokens, password reset, and authenticator enrollment.
- Browser sessions use HttpOnly cookies. A future mobile app can request bearer tokens with `X-Client: mobile`.
- Organizations are isolated. A member cannot read another organization's private supplier notes.
- Public catalogue, categories, and supplier storefronts are loaded from the database.
- Address book, notifications, and the contact form.
- OpenAPI docs at `/api/docs/`.

Orders, payments, professional booking, facility procurement, and the Flutter app are later slices. See [docs/implementation-plan.md](docs/implementation-plan.md).

## Run it locally

Details and the Render deploy are in [docs/deploy-render.md](docs/deploy-render.md).

```powershell
docker compose up -d
copy .env.example .env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

In another terminal, from the repository root:

```powershell
npm install
npm run dev
```

Open `http://localhost:3000`. After seeding, every sample account uses `Demo-Only-Change-Me-1`.

## Free cloud demo

[docs/deploy-render.md](docs/deploy-render.md) deploys the site, the API, and Postgres on Render's free plan with `render.yaml`. The free database expires after 30 days, and the web services sleep when idle.

## Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

From the repository root:

```powershell
npm run typecheck
npm run lint
```
