# Finance module architecture

SRAJ NOVA keeps one agency and many client organisations. Finance is the Django app `modules.finance`, mounted at `/api/v1/`. The web app reads it through the existing JSON proxy. This document describes the module that exists and the boundary for the next one. It does not add a second ledger.

## Current posting path

1. `rebuild_week_invoices` writes `ClientInvoice` from filled shifts, hourly rates, and the contract fee rate. A posted invoice is left unchanged.
2. `post_week_invoices` writes a balanced journal for each invoice in the current week. A second post reverses the open journal, then writes a new one.
3. `record_receipt` writes cash and accounts receivable, then stores `ClientReceipt` pointing at that journal.
4. `books_snapshot` and `trial_balance` read the lines. They do not recompute wages.

Employment cost is credited to wages payable (2000). The agency fee is credited to revenue (4000). The debit is accounts receivable for the invoice total. That treats the wage as an amount the agency still owes, and the fee as the agency’s income. It is not a full payroll distribution.

## Permissions today

| Role | Finance summary | Books, post, receipt | Command cash |
| --- | --- | --- | --- |
| Agency owner, operations, finance | All clients | Yes | Yes |
| Client user | Own client, no cash | No | No |
| Employee | No | No | No |

The twelve roles named in the upgrade brief (finance director, controller, payroll officer, payable and receivable officers, auditor, and the rest) are not users in `AgencyRole`. Adding the names without an authorisation matrix would not create a maker-checker. Payroll preparation and payroll approval must be different people before a payroll run can be executed. That split waits until a payroll-run table exists.

## Foundation added with this upgrade

`ledger_position` classifies posted lines into asset, liability, equity, and income balances. It is exposed at `GET /api/v1/accounting/position/` to agency roles. Operating profit is null. The response states that no expense account has been posted, so fee revenue must not be read as net profit.

## Next module boundary

New tables, when built, hang off the existing journal:

- A manual journal is still a `JournalEntry` plus lines, with a status of draft until approval. Posted rows stay immutable.
- A payroll run produces journals that split gross expense, employee deductions, employer contributions, and net payable. Those accounts do not exist yet and must not be filled with estimated Ghana rates.
- A receipt allocation table can split one receipt across invoices. The current receipt remains one invoice, one journal.
- Bank and mobile-money accounts are settlement records. Until a provider is integrated, the UI must keep the current sentence: no bank or mobile-money settlement has been executed.

Reports in a later phase read `ledger_position` and the trial balance. They must not sum dashboard cards into a second set of totals.
