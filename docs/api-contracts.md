# API contracts

Base path: `/api/v1`

OpenAPI: `/api/schema/` and `/api/docs/`

## Envelope

Success:

```json
{ "data": {}, "meta": {} }
```

List `meta`:

```json
{ "count": 0, "page": 1, "page_size": 20, "pages": 1 }
```

Error:

```json
{ "error": { "code": "validation_error", "message": "Some fields need attention.", "details": {} } }
```

Common codes: `validation_error`, `unauthenticated`, `forbidden`, `not_found`, `csrf_failed`, `rate_limited`, `invalid_credentials`, `mfa_required` (returned as data, not an error), `mfa_enrollment_required`, `invalid_token`.

## Authentication

| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| GET | `/auth/csrf/` | Public | Returns `csrf_token` and sets the CSRF cookie. |
| POST | `/auth/register/` | Public + CSRF | Creates a customer. Browser responses set cookies. |
| POST | `/auth/login/` | Public + CSRF | Generic failure text. |
| POST | `/auth/mfa/verify/` | Public + CSRF | Exchanges `mfa_token` and TOTP code for a session. |
| POST | `/auth/mfa/enroll/` | Session or `enrollment_token` | Starts TOTP. Secret is returned once. |
| POST | `/auth/mfa/confirm/` | Session or `enrollment_token` | Confirms TOTP. |
| POST | `/auth/logout/` | CSRF | Clears cookies and blacklists the refresh token. |
| POST | `/auth/refresh/` | CSRF or mobile | Rotates the refresh token. |
| GET, PATCH | `/auth/me/` | Session or bearer | Profile. Email and role are read-only. |
| POST | `/auth/verify-email/` | Public + CSRF | One-time token from the email. |
| POST | `/auth/resend-verification/` | Session | Sends another verification email. |
| POST | `/auth/password-reset/` | Public + CSRF | Always returns the same message. |
| POST | `/auth/password-reset/confirm/` | Public + CSRF | Sets a new password. |

Browser clients omit `X-Client`. Access and refresh fields in the body are `null`; the tokens are cookies.

Mobile clients send `X-Client: mobile`. Login and refresh return `access` and `refresh` in `data` and do not set cookies. Later calls send `Authorization: Bearer <access>`. Bearer calls do not use CSRF.

Login data:

```json
{
  "user": {},
  "mfa_required": false,
  "enrollment_required": false,
  "access": null,
  "refresh": null,
  "mfa_token": null
}
```

When MFA is already enabled, `mfa_required` is true and no access cookie or access token is issued. When a privileged account must enroll first, the response is HTTP 403 `mfa_enrollment_required` with `details.enrollment_token`.

## Account

| Method | Path | Notes |
| --- | --- | --- |
| GET, POST | `/account/addresses/` | Current user only. |
| PATCH, DELETE | `/account/addresses/{id}/` | Missing and other users' rows are 404. |
| GET | `/account/memberships/` | Active memberships for the current user. |
| GET | `/account/notifications/` | Current user only. |
| PATCH | `/account/notifications/{id}/` | Marks the notice read. |

## Organizations

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/organizations/{id}/` | Members, or a platform admin. Admin reads write an audit row. Non-members receive 404. |

Creating an organization through the API is part of supplier registration, which is not exposed yet. The service function exists for that slice.

## Catalogue

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/catalog/categories/` | Includes checkout policy and product counts. |
| GET | `/catalog/products/` | Query: `q`, `category`, `supplier`, `ordering` (`name`, `price`, `-price`), `page`, `page_size`. |
| GET | `/catalog/products/{slug}/` | 404 when the product has no public listing. |
| GET | `/catalog/suppliers/` | `demo` and `verified` suppliers on active organizations. |
| GET | `/catalog/suppliers/{slug}/` | Public profile and listings. |
| GET | `/catalog/suppliers/{slug}/internal/` | Members only. Returns `internal_notes`. |

`can_purchase` is false for every sample listing. `purchase_block_reason` explains the block in plain language.

Prices are decimal strings with currency `GHS`.

## Support and operations

| Method | Path | Notes |
| --- | --- | --- |
| POST | `/support/inquiries/` | Public, throttled. |
| GET | `/health/` | Database and Redis checks. HTTP 503 when the database is down. |
| GET | `/` | Service name and docs link. Not under `/api/v1`. |

## Planned endpoints

These are not registered. Clients must not call them.

- Supplier registration, credential upload, and admin verification decisions.
- Cart, checkout, payment intents, and payment webhooks.
- Merchant order acceptance and shipment updates.
- Professional profiles, availability, and appointment holds.
- Facility requisitions, approvals, RFQs, and purchase orders.
- Admin audit log queries.

Payment webhooks will require a provider signature and an idempotency record. Appointment holds will accept an idempotency key.
