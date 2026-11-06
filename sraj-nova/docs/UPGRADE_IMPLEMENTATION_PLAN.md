# Upgrade implementation plan

The application is a modular Django and Next.js system under `sraj-nova/`. Render serves it from the existing `medisource-gh-web` and `medisource-gh-api` services. This plan does not rebuild those apps and does not add a Render service.

## Phase 1 — design system and command center

In this delivery.

- Retoken `globals.css`, the rail, gauges, and the sign-in panel.
- Rebuild `src/app/command/page.tsx` around stored counts and stored money.
- Leave every existing route and write action in place.

## Phase 2 — ledger position and executive board

Ledger position is live: `GET /api/v1/accounting/position/` classifies posted lines and leaves operating profit null.

The command center now also reads a `board` payload:

- Seven days of stored shifts. A future day is scheduled, not absent.
- Invoice weeks and this week’s fee and wages by client. Fee revenue is not labelled as profit.
- A factory staffing grid of filled and open posts.
- Recent punches, staffing requests, journals, and receipts in the user’s scope.
- Unpaid invoices. Payroll approvals stay an empty list because no payroll run exists.

## Phase 3 — chart, periods, manual journals

In this delivery.

- Account groups Assets, Liabilities, Equity, and Income. The five system accounts keep their codes and are linked to a group.
- One open fiscal year covers 1 January to 31 December. Journals with no period are assigned to the year that contains their date.
- A manual journal is saved as a draft and is excluded from the trial balance and from cash. Posting requires equal debits and credits and an open period.
- A posted journal is reversed by a new journal. Its original lines stay. Closing the period refuses later posts, and the period can be reopened.

## Phase 4 — receivables, payables, treasury, payroll journals

Not started. Extend receipts with allocations. Add suppliers only with approval limits. Add bank matching as an unmatched queue. Payroll journals wait on a validated Ghana rule pack. No provider integration, so no “paid” status.

## Phase 5 — statements and budgets

Not started. Profit and loss, balance sheet, and cash flow are generated from `ledger_position` once expense accounts and a close exist. Until then the position endpoint is the statement. PDF and Excel wait until those statements balance. Budgets compare to the same ledger lines.

## Phase 6 — heavier graphics

Not started. ECharts and Motion load only for series returned by the API. React Flow loads only for a stored approval graph.

## Phase 7 — verification

Run `modules/finance/tests/test_books.py`, `modules/operations/tests/test_actions.py`, and `modules/organization/tests/test_workforce_finance.py` after this delivery. Typecheck the web app. Open the sign-in and command screens in the browser.

Do not migrate destructive changes. Do not commit MediSource files that sit outside `sraj-nova/`.
