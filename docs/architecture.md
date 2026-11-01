# MediSource GH architecture

## Style

The backend is a modular monolith. Domain modules share one PostgreSQL database, one Django process, and one versioned HTTP API. Modules call each other through explicit service functions and foreign keys, not through hidden cross-imports of views.

The web clients are Next.js applications. `apps/marketplace-web` is the public site and customer account. `apps/business-web` and `apps/admin-web` are reserved for the supplier, facility, and platform consoles. `apps/mobile-flutter` is reserved for the future Dart clients. Those clients will use the same `/api/v1` contract.

```text
Browser (Next.js)  ---- cookie session + CSRF ----+
                                                   |
Future Flutter app ---- bearer tokens -------------+--> Django REST API --> PostgreSQL
                                                   |                     --> Redis / Celery
                                                   +--> S3-compatible media (later)
```

## Repository

```text
apps/marketplace-web     Public site and customer account
apps/business-web        Reserved
apps/admin-web           Reserved
apps/mobile-flutter      Reserved
backend/config           Settings, URLs, Celery, WSGI
backend/common           API envelope, auth, pagination, health
backend/modules          Domain modules
packages/ui              Shared React components
packages/api-client      Typed HTTP client
packages/shared-types    Response types
packages/design-tokens   Colour and type tokens
infrastructure           Docker and operations notes
docs                     Architecture and operating rules
```

## Backend modules

| Module | Responsibility | State |
| --- | --- | --- |
| identity | Users, sessions, MFA, addresses | Implemented |
| organizations | Tenants and memberships | Implemented |
| catalog | Master products, listings, category policy | Implemented |
| audit | Append-only security and admin events | Implemented |
| notifications | Account notices and contact inquiries | Implemented |
| credentialing | Document intake and review decisions | Planned |
| suppliers | Supplier onboarding beyond the profile | Planned |
| inventory | Warehouses, batches, expiry, reservations | Planned |
| marketplace | Cart and customer orders | Planned |
| procurement | Requisitions, approvals, RFQs, POs, GRN | Planned |
| professionals | Professional profiles and specialties | Planned |
| scheduling | Availability and slot holds | Planned |
| appointments | Booking transactions | Planned |
| home_care | Eligible home services | Planned |
| facilities | Facility directory and departments | Planned |
| payments | Intents, webhooks, ledger | Planned |
| settlements | Merchant payables and payouts | Planned |
| logistics | Shipments and proof of delivery | Planned |
| analytics | Reporting reads | Planned |

## Request rules

- JSON envelope: `{ "data": ..., "meta": ... }`.
- Errors: `{ "error": { "code", "message", "details" } }`.
- Lists use page, page size, count, and pages in `meta`.
- Identifiers are UUIDs. Public catalogue URLs also use stable slugs.
- Writes that change money, stock, or bookings will run inside `transaction.atomic` with row locks or exclusion constraints. The catalogue read models already use constraints for non-negative stock and price.
- Default permission is authenticated. Public reads opt in with `AllowAny`.

## Authentication

Browsers call the API with `credentials: "include"`.

- `ms_access` is an HttpOnly cookie for API calls.
- `ms_refresh` is an HttpOnly cookie scoped to `/api/v1/auth/`.
- Unsafe browser calls send `X-CSRFToken`, issued by `GET /api/v1/auth/csrf/`.
- Mobile clients send `X-Client: mobile` and receive bearer tokens in the body. A browser cannot attach that custom header cross-origin without a CORS preflight, so the header is not a substitute for a bearer secret on hostile origins.

Privileged roles (`platform_admin`, `finance_officer`) must pass TOTP when `MFA_REQUIRED_FOR_PRIVILEGED` is true. Production settings turn that flag on. Enrollment uses a short-lived signed token that cannot call other endpoints.

## Tenancy

An organization is the tenant for a supplier or a facility. Membership is the only normal path to private fields such as supplier internal notes. A platform administrator does not receive those notes through the member endpoint. A later support tool, if added, has to write an audit event for each disclosure.

## Catalogue

Master product specifications live once. A supplier listing stores commercial terms only: price, stock, warehouse label, minimum quantity, lead time, and delivery zones. Category policy is a separate row so commercial checkout can be closed without deleting the product.

## Payments (planned)

Provider credentials stay in the environment. The application will create a payment intent, accept only signed webhooks, and store an idempotency key. The ledger will separate gross value, discounts, tax, delivery, provider fees, commission, merchant payable, refunds, and payout status. Sandbox mode is the default until a provider is configured. This milestone does not mark anything as paid.

## Appointments (planned)

A slot hold and a confirmed booking will be the same resource in one transaction. PostgreSQL will reject overlapping active ranges for a professional or room. Expired holds will be released by a Celery task. Credential expiry will remove the related services from the bookable set.

## AI (planned)

Provider-agnostic interfaces can sit beside search and analytics. They are not on the transaction path. No model output can flip verification, payment, or clinical status.

## Runtime

Local development runs PostgreSQL 16 and Redis 7 in Docker, Django on port 8000, and Next.js on port 3000. Tests use SQLite unless `USE_POSTGRES_TESTS=true`, so the suite can run before Docker is installed. Continuous integration sets that flag and `DATABASE_URL` to PostgreSQL.

Celery is configured with Redis. Tests run tasks eagerly. No business workflow depends on a worker yet.

Media uploads are not exposed. When they are, credential files go to a private bucket, with content-type and size checks, and never to the public product image path.
