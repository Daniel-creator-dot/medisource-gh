# Financial workflows

These are the workflows the application can complete today, and the ones it must refuse.

## Invoice week

An agency user opens Finance and rebuilds the worksheet, or assigns a worker on Coverage, which rebuilds the same week. The invoice is hours on filled shifts times the stored hourly rate, plus the contract fee. Unfilled shifts add nothing. A client user can read their own invoice and cannot rebuild.

## Post and reverse

Books → Post week. Each current-week invoice with a total above zero gets one balanced journal. Posting again reverses the open journal and writes a replacement. The first journal’s lines stay as they were. A client user receives 403.

## Receipt

Agency user enters an invoice, an amount, and a reference. The amount must be greater than zero and no more than the outstanding balance. The invoice must already be posted. The reference cannot repeat. The journal is Dr cash, Cr accounts receivable. Nothing is sent to a bank or a mobile-money wallet.

## What the command center may show

- Weekly gross wages, agency fee, outstanding invoices, and recorded cash, from the summary above.
- On duty, late, and absent, from attendance events on today’s shifts.
- Certifications expiring within 60 days, from stored certification dates.

## What it must not show as a number

- Net pay, PAYE, employee pension, employer pension, VAT.
- A salary payment date. No payroll run is stored.
- Operating profit. Fee revenue is not profit while wage expense is not an account.
- A payroll trend for weeks that have no invoice rows.
- A bank balance. Cash is the 1000 account, or the cash-movement sum when that account has no lines.

## Future maker-checker

When payroll runs exist, the user who prepares the run cannot approve it. Approval writes the journals. Rejection writes an audit event and no journal. Reversal is a new journal, not an edit. That workflow is not available, and the Actions screen does not pretend to approve payroll.
