# Accounting gap analysis

Inspection date: 6 November 2026. Source of truth: `modules/finance/models.py`, `modules/finance/ledger.py`, `modules/finance/services.py`, and `docs/GHANA_PAYROLL_RULES.md`.

## Implemented and tested

| Capability | Where | Limit |
| --- | --- | --- |
| Chart of five accounts | `ledger.CHART` codes 1000, 1100, 2000, 3000, 4000 | Fixed in code. Not a user-editable chart. |
| Balanced journals | `_save_entry` refuses unequal or zero totals | No draft state. An entry is posted as soon as it is saved. |
| Reversal instead of edit | `post_week_invoices` reverses open invoice journals | Original lines are not updated. |
| Opening cash | Dr 1000 / Cr 3000, memo “Sample opening cash balance”, once | Demonstration book entry, not a bank balance. |
| Cost-plus weekly invoice | Hours × stored rate, plus contract fee rate | One invoice per client per week. Posted invoices are not rebuilt. |
| Client receipt | Dr 1000 / Cr 1100, cannot exceed outstanding, unique reference | One invoice per receipt. Not an allocation table. Not a bank or mobile-money settlement. |
| Trial balance | Sum of journal lines, debit total must equal credit total | Agency roles only. |
| Aging | Outstanding invoices bucketed from `week_start` | Current, 8 to 30 days, over 30 days. |
| Cash on the finance summary | Ledger cash when cash lines exist | Agency roles only. Client users do not see cash. |

Seed-week expectation used by tests, before any extra assignment: gross wages 606.00, agency fee 70.20, invoices 676.20, opening cash 2500.00, trial balance 3176.20 after posting.

## Partial

- Accounts receivable is the weekly `ClientInvoice` plus receipts. There are no credit notes, disputes, statements, or recurring schedules.
- Payroll in the ledger is a credit to wages payable for employment cost. There is no wage-expense account, so a profit figure cannot be closed.
- Roles that can touch money are agency owner, agency operations, and agency finance. There is no maker-checker split between them.

## Not implemented

Accounts payable, suppliers, expense claims, bank accounts, statement import, reconciliation, mobile money, payment batches, budgets, fiscal years, accounting periods, manual journals, journal approval, general-ledger register by account, year-end close, cost centers, PDF or Excel export, and every statutory amount.

PAYE, SSNIT Tier 1, Tier 2, employer contributions, VAT, net pay, and salary payment status are intentionally absent. `docs/GHANA_PAYROLL_RULES.md` forbids treating weekly gross as a statutory result. Rates must not be hardcoded. A Ghana payroll professional has to validate effective-dated rules before any live run.

`statutory_engine` on the command center is `not_active`. `estimated_net_payroll` and `statutory_liabilities` are null.
