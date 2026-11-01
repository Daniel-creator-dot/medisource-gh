# Implementation plan

Work lands in vertical slices. A slice is done when models, migrations, authorized APIs, the relevant UI, and tests are in place, and the UI is talking to the database.

## Milestone 1 — Foundation (current)

- Documents in `docs/`.
- Docker Compose for PostgreSQL, Redis, and the API.
- Django project, identity, organizations, catalogue, audit, notifications.
- Next.js marketplace, shared tokens, UI package, and API client.
- Homepage and catalogue on seeded sample data.
- Auth, MFA, tenancy, and catalogue tests.

## Milestone 2 — First commercial slice

1. Supplier registration and credential upload to private storage.
2. Admin review that sets `verified` or `rejected` and writes an audit event.
3. Supplier creates a listing on an eligible master product.
4. Customer searches, opens the product, and adds it to a cart.
5. Checkout re-checks policy and stock, splits merchant orders, and opens a sandbox payment intent.
6. A signed sandbox webhook settles the ledger. A repeated webhook is a no-op.
7. Supplier sees the merchant order, accepts it, and moves it to processing and then fulfilled.
8. Customer sees the updated status.

Tests that must exist before this slice is called done:

- A second supplier cannot read the first supplier's order or notes.
- Two concurrent checkouts cannot reserve the last unit twice.
- A forged or replayed webhook does not mark an order paid.
- A pharmaceutical or `demo` line cannot be checked out.
- An approval or status transition that skips a step is rejected.

## Milestone 3 — Professionals and appointments

- Credential upload, manual review, expiry, and suspension.
- Public profiles only after verification.
- Services, locations, availability, holds, and confirmed bookings.
- Exclusion constraint against double booking.
- Cancellation and reschedule.
- Reminder task via Celery.

## Milestone 4 — Facility procurement

- Departments, invitations, and roles.
- Requisitions, thresholds, and approval chains.
- RFQ, quotation, purchase order, partial goods receipt, and invoice differences.
- Buyer cannot see another facility's records.

## Milestone 5 — Money, logistics, and admin centre

- Ledger, commissions, refund review, and settlements.
- Shipment states, proof of delivery, returns, and an adapter interface for couriers.
- Admin users, verification queues, category policy, disputes, and audit search.
- Dashboards that read aggregated tables, with sample charts labelled when they are not live.

## Milestone 6 — Flutter

- Generate or hand-maintain Dart clients from the OpenAPI schema.
- Reuse bearer token, idempotency, and media upload contracts.
- Do not fork business rules into the mobile app.

## Local quality bar for every slice

- `python manage.py check`
- `pytest` from `backend/`
- `npm run typecheck` and `npm run lint` from the repository root
- Browser pass on the pages that changed, when a dev server is available

## Explicit non-goals until their slice

- Microservices, a separate payment service, or a second database.
- Automatic verification from a document upload.
- Live Mobile Money or card charges.
- Invented clinicians, ratings, or regulatory badges.
