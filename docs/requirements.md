# MediSource GH requirements

MediSource GH is a healthcare marketplace and procurement platform for Ghana. This document records product requirements for the modular monolith. It is an engineering specification, not a regulatory approval.

## Users

| Actor | Needs |
| --- | --- |
| Customer | Browse eligible products, manage an account, and later place orders and book care. |
| Supplier | Publish listings against master products, manage stock, and fulfil orders after verification. |
| Facility buyer | Run procurement with departments, budgets, approvals, RFQs, and goods receipt. |
| Healthcare professional | Publish only services that match a reviewed, unexpired credential. |
| Platform administrator | Verify suppliers and professionals, configure regulatory category policy, and reconcile money. |
| Finance officer | Review payments, refunds, commissions, and settlements. |

## Product principles

- One Django API serves the web applications and the future Flutter clients.
- Business rules live in backend services and database constraints.
- A customer order may later split into one merchant order per supplier.
- Checkout exists only for categories whose regulatory policy explicitly allows it.
- Prescription and unrestricted medicine sales stay disabled until the legal basis and controls exist.
- Sample catalogue rows are fictional and cannot be purchased.
- Uploading a credential never verifies a professional by itself.
- An unverified payment redirect is never treated as a successful payment.
- AI may assist search and analytics later. It cannot approve payment, diagnose, prescribe, or verify a professional.

## Milestone 1 scope (this repository state)

Implemented:

- Monorepo, Docker Compose, and environment-based configuration.
- Django 5.2 API with PostgreSQL, Redis, and Celery wiring.
- Customer registration, login, logout, refresh, email verification, and password reset.
- Cookie sessions for the browser and bearer tokens for a future mobile client.
- TOTP MFA, required for privileged roles when `MFA_REQUIRED_FOR_PRIVILEGED` is on.
- Organizations, memberships, and cross-tenant isolation.
- Master catalogue, supplier profiles, listings, and category regulatory policy.
- Public catalogue and supplier directory backed by the database.
- Account profile, address book, and in-app notifications.
- Contact inquiries.
- Audit records for authentication and sensitive reads.
- Marketplace homepage, catalogue, account, and informational pages.
- Automated API tests.

Not implemented yet, and not presented as working in the interface:

- Supplier onboarding workflow and admin verification screens.
- Cart, multi-supplier checkout, sandbox payment, and order status.
- Inventory reservation, warehouses, batch, and expiry tracking.
- Professional credential review and appointment booking.
- Facility procurement, approvals, RFQs, and purchase orders.
- Settlements, refunds, disputes, and logistics provider integrations.
- Admin control centre beyond Django's technical admin at `/django-admin/`.
- Flutter applications.

## Regulatory checkout rule

A listing is purchasable only when all of the following are true:

1. The supplier organization is active.
2. The supplier verification status is `verified` (the `demo` status is never purchasable).
3. The listing is active and stock covers the minimum order quantity.
4. The category policy has `checkout_enabled` and does not require an authorization step that the platform cannot yet perform.

The seeded category `authorized-pharmaceuticals` remains checkout disabled.

## Acceptance for later vertical slices

The first commercial slice is complete only when a verified supplier can publish an eligible listing, a customer can place an order, a sandbox payment is confirmed by a verified webhook, and both parties see the same database-backed status. That slice needs its own tests for idempotency, inventory races, and duplicate webhooks.
