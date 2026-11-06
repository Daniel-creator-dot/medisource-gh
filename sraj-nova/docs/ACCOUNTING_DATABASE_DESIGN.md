# Accounting database design

Existing tables are UUID primary keys and `Decimal` money with two places. Do not replace them.

## Tables in the database now

- `finance_cashmovement` — dated amount and a unique description. Opening cash is also a journal. The movement row is not the ledger.
- `finance_clientinvoice` — client, week start, employment cost, agency fee, currency GHS, status. Unique on client and week.
- `finance_account` — code, name, account type (`asset`, `liability`, `equity`, `income`). Codes 1000, 1100, 2000, 3000, 4000.
- `finance_journalentry` — date, memo, optional invoice, optional `reverses` self-link.
- `finance_journalline` — debit and credit, both non-negative, exactly one side positive.
- `finance_clientreceipt` — client, invoice, one journal, date, amount, unique reference.

There is no database constraint that a journal’s debits equal its credits. `_save_entry` enforces that in a transaction before the rows are written. A later migration can add a deferred constraint trigger. It is not in this phase, because the current rows already balance and a trigger needs a database-specific check on PostgreSQL and SQLite.

## Tables designed, not created

Creating empty copies of these tables would not make the workflows real. They are the next migration, after the posting rules in `FINANCIAL_WORKFLOWS.md` are implemented and tested.

| Future table | Purpose | Rule |
| --- | --- | --- |
| `account_group` | Groups and parent accounts | Nullable parent. Account keeps its code. |
| `fiscal_year`, `accounting_period` | Open and closed dates | A post into a closed period is rejected. Existing entries need an open period backfilled, not a rewrite. |
| `journal_approval` | Maker-checker | Status draft, approved, posted. Posted lines immutable. |
| `supplier`, `supplier_bill`, `supplier_payment` | Payables | Bill total equals lines. Duplicate supplier reference is rejected. |
| `receipt_allocation` | One receipt, many invoices | Allocations cannot exceed the receipt or the invoice outstanding. |
| `bank_account`, `bank_statement_line`, `reconciliation` | Treasury | A line matches at most one journal line. No provider settlement flag until an integration exists. |
| `budget`, `budget_line` | Budgets | Variance is budget minus ledger activity for the same account and period. |
| `payroll_run`, `payroll_liability`, `statutory_remittance` | Payroll accounting | Amounts come from a versioned rule set. No rate column is seeded with a guessed Ghana band. |
| `cost_center` | Site or department | Optional on journal lines. Historical lines stay unassigned. |
| `financial_audit_event` | Append-only | Who approved, reversed, or rejected. No updates. |

`clients` already exist on `organization.Client`. Invoice lines are not split today: employment cost and agency fee are columns on `ClientInvoice`. A line table can be added later without deleting those columns, and the journal must still be traceable to the invoice id.
