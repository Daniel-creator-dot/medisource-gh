# Deployment guide

Local development uses SQLite on port 8010 and the command center on port 3010.

The Render blueprint reuses the existing services `medisource-gh-api`, `medisource-gh-web`, and `medisource-gh-db`. The hostnames stay the same so no extra Render service is created. The application served there is SRAJ NOVA.

- Web: https://medisource-gh-web.onrender.com
- API: https://medisource-gh-api.onrender.com

The demonstration deploy leaves agency-owner authenticator enrollment off so the sample owner can sign in. Turn `MFA_REQUIRED_FOR_AGENCY_OWNER` on before any live payroll use. The seed command loads synthetic records only because `FORCE_SEED_DEMO` is set.

Free Render web services sleep after 15 minutes. The free Postgres database expires 30 days after it was created.
