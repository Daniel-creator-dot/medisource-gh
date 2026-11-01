# Security model

## Authentication and session

- Passwords are hashed by Django's password hashers and must be at least 12 characters.
- Login failures use one message for unknown emails and wrong passwords.
- Browser tokens are HttpOnly cookies. JavaScript reads neither the access nor the refresh token.
- The refresh cookie path is `/api/v1/auth/` so catalogue requests do not carry it.
- Refresh tokens rotate and the previous token is blacklisted.
- Mobile access tokens are short-lived JWTs. The client stores them; the web app does not put them in `localStorage`.
- Email verification and password reset tokens are random, stored only as SHA-256 hashes, and expire. Reset links last one hour. Verification links last 24 hours.
- TOTP secrets are encrypted with Fernet before they are stored. The key is derived from `DJANGO_SECRET_KEY`. Rotating that key invalidates enrolled factors and requires re-enrollment.
- Production settings require MFA before a platform admin or finance officer receives a session.

## CSRF, CORS, and browsers

- Django REST framework does not enforce CSRF on API views by itself. `CookieAuthCsrfMiddleware` enforces it for browser API writes.
- Bearer requests and `X-Client: mobile` skip CSRF. The mobile header is a non-simple header, so a foreign website cannot send it unless we explicitly allow that origin.
- `CORS_ALLOWED_ORIGINS` is an explicit list. Credentials are allowed only for those origins.
- Cross-origin browser logins must also match `CSRF_TRUSTED_ORIGINS`.

## Authorization

- Default API permission is authenticated.
- Querysets for addresses, notifications, and memberships filter on the current user.
- Private supplier notes require an active membership on that supplier's organization. Missing rows and forbidden rows both return 404 so callers cannot enumerate slugs they cannot access through a different status code. Public supplier slugs are already public.
- Platform admin access to an organization record is audited. It does not include supplier internal notes.
- The registration payload cannot set `platform_role`, `is_staff`, or `is_superuser`.

## Abuse controls

- Login, registration, MFA, and password reset use the `auth` throttle.
- Contact inquiries use a tighter `contact` throttle.
- Tests raise those limits so the suite does not depend on the clock. The production numbers are in `config.settings.base`.

## Data and secrets

- `DJANGO_SECRET_KEY`, database URLs, and future payment secrets come from the environment.
- `.env` is gitignored. `.env.example` contains placeholders.
- Demo accounts are labelled `is_demo_account` and the seed command refuses to run when `DEBUG` is false unless `FORCE_SEED_DEMO` is set.
- Audit metadata must never include passwords, refresh tokens, or TOTP secrets.
- Client IP is taken from `REMOTE_ADDR`. Forwarded headers are not trusted until a proxy is configured deliberately.

## Files, payments, and health data

- There is no upload endpoint in this milestone. The future rule is: allow-list content types, limit size, store credentials outside the public bucket, and scan before a reviewer opens the file.
- There is no payment endpoint. A redirect back from a gateway will not update an order. Only a verified webhook will.
- This milestone stores account data and catalogue content. It does not store clinical records. Appointment and home-care data, when added, will be authorized by role and relationship, not by hiding buttons.

## Transport and headers

- Production settings redirect to HTTPS, mark cookies secure, and send HSTS.
- Local HTTP is allowed only when `DEBUG` is true, which also leaves auth cookies non-secure so browsers will store them.
- Clickjacking protection is deny. Content type sniffing is disabled.

## What still needs a control before production

- Real SMTP instead of the console email backend.
- Key management that can rotate the MFA encryption key without a flag day, or a documented re-enrollment plan.
- A reverse proxy that sets a trusted client IP.
- Database backups and restore drills.
- Private object storage.
- Admin review screens whose privileged actions are individually audited.
- Rate limits in front of the app, not only inside Django.
- Dependency and image update policy in CI.
