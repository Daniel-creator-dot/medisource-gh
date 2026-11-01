# Business workflows

Workflows marked **live** run on the API today. Workflows marked **designed** are the target and are not available in the product yet.

## Customer account (live)

1. A person registers with an email and password. The account role is customer. Privileged flags cannot be set from the form.
2. The API stores a hashed email-verification token and sends the link. In local development the message is printed by the console email backend.
3. The browser receives HttpOnly session cookies. The customer can update a profile, save addresses, and read notifications.
4. Password reset always answers with the same sentence, whether or not the email exists.
5. If the customer later enables an authenticator, password login stops issuing a session until the one-time code is accepted.

## Browse the catalogue (live)

1. Public pages request categories, products, and suppliers.
2. Only active listings from `demo` or `verified` suppliers on active organizations are returned.
3. Pending, rejected, and suspended suppliers stay out of the public directory.
4. Each listing includes `can_purchase` and a plain-language block reason.
5. Sample rows remain visible for development and cannot be bought.

## Supplier joins (designed)

1. A supplier submits a business profile and credential files.
2. The organization is created in `pending` status. Nothing is public.
3. A platform admin reviews the file and records a decision. Upload alone does not verify the supplier.
4. Approval sets `verified`, writes an audit event, and allows eligible listings.
5. Suspension hides listings and stops new orders. It does not delete the ledger.

## Publish a listing (designed, catalogue model is live)

1. The supplier selects a master product. They do not copy the clinical specification into their own record.
2. They set price, currency, stock, warehouse, minimum quantity, lead time, and delivery zones.
3. The API rejects the listing when the category policy forbids that supplier type or the product is inactive.
4. Stock changes that belong to an order will reserve quantity inside a transaction so two checkouts cannot sell the same unit.

## Order and payment (designed)

1. The customer checks out only purchasable lines. The server re-checks policy, verification, stock, and price. It does not trust the browser total.
2. Lines are grouped into merchant orders, one supplier per merchant order, under one customer order.
3. A payment intent is created in sandbox or live mode. The browser return URL does not settle the payment.
4. A verified webhook with a new idempotency key marks the intent paid and writes ledger rows: gross, discount, tax, delivery, fee, commission, merchant payable.
5. Duplicate webhooks do not post the ledger twice.
6. The supplier accepts and ships. Partial delivery updates the merchant order without closing the remainder.
7. The customer sees the same status the supplier updated.

## Professional booking (designed)

1. Search returns professionals whose required credential is reviewed, unexpired, and not suspended.
2. The customer chooses a service the credential allows, a place or remote mode, and an open slot.
3. The API takes a short hold in a transaction. A database exclusion constraint rejects a second active booking on that resource and range.
4. Payment or a facility guarantee confirms the hold. If the hold expires, the slot returns to the calendar.
5. Cancellation follows the policy stored on the service. Reschedule is a new hold plus release of the old row, in one transaction.
6. A credential that expires or is suspended removes future bookable services. Existing bookings are flagged for a person to resolve. The software does not silently invent a replacement clinician.

## Facility procurement (designed)

1. Staff submit a requisition against a department and a budget.
2. Approval steps follow configured thresholds and roles. The requester cannot approve their own requisition above the self-approval limit.
3. Buyers compare verified suppliers, issue an RFQ, and accept a quotation.
4. A purchase order is sent. Goods receipt records partial quantities. Invoice match highlights price and quantity differences.
5. Invalid transitions, such as approving a rejected requisition without a new submission, are rejected and tested.

## Platform administration (designed)

1. Admins work in the admin application, not by editing the public site.
2. Verification, refund, commission, and category-policy changes write an audit row with the actor and the before/after value.
3. No admin action marks a payment successful or a clinician verified without that logged decision.
4. Financial corrections are reversing ledger entries, not silent edits to posted rows.
