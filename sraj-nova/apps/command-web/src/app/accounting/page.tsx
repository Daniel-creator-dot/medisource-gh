import { PostWeek } from "@/components/post-week";
import { RecordReceipt } from "@/components/record-receipt";
import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Books = {
  note: string;
  accounts: { code: string; name: string; account_type: string }[];
  journals: { id: string; entry_date: string; memo: string; reversal: boolean; lines: { code: string; name: string; debit: string; credit: string }[] }[];
  trial_balance: { rows: { code: string; name: string; account_type: string; debit: string; credit: string }[]; total_debit: string; total_credit: string; balanced: boolean };
  aging: { invoice_id: string; client_name: string; week_start: string; outstanding: string; bucket: string }[];
  open_invoices: { id: string; client_name: string; outstanding: string; posted: boolean }[];
  receipts: { reference: string; client_name: string; amount: string; received_on: string }[];
};

export default async function AccountingPage() {
  const result = await apiGet<Books>("/accounting/");
  const books = result.data;
  return (
    <Shell>
      <p className="text-sm font-semibold tracking-[0.16em] text-[var(--orange)]">BOOKS</p>
      <h1 className="display mt-1 text-4xl font-bold">Accounting</h1>
      {result.status === 403 || !books ? (
        <p className="mt-3">{result.message || "The books are limited to agency staff."}</p>
      ) : (
        <div className="mt-6 space-y-6">
          <p className="text-sm text-[var(--muted)]">{books.note}</p>
          <section className="panel p-4">
            <h2 className="display text-2xl font-bold">Chart of accounts</h2>
            <div className="sheet mt-3">
              <table className="min-w-full text-left text-sm">
                <thead className="border-b border-[var(--line)] text-[var(--muted)]"><tr><th className="px-3 py-2">Code</th><th className="px-3 py-2">Account</th><th className="px-3 py-2">Type</th></tr></thead>
                <tbody>
                  {books.accounts.map((account) => (
                    <tr key={account.code} className="border-b border-[var(--line)]"><td className="px-3 py-2">{account.code}</td><td className="px-3 py-2">{account.name}</td><td className="px-3 py-2">{account.account_type}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <section className="panel p-4">
            <h2 className="display text-2xl font-bold">Journals</h2>
            <p className="mt-1 text-sm text-[var(--muted)]">Posting an invoice debits accounts receivable and credits wages payable and agency fee revenue. Posting again reverses the earlier entry and writes a new one.</p>
            <div className="mt-3"><PostWeek /></div>
            <ul className="mt-4 space-y-3 text-sm">
              {books.journals.map((entry) => (
                <li key={entry.id} className="rounded-xl bg-[var(--canvas)] px-3 py-2">
                  <p className="font-medium">{entry.entry_date} · {entry.memo}{entry.reversal ? " · reversal" : ""}</p>
                  <ul>{entry.lines.map((line) => <li key={`${entry.id}-${line.code}-${line.debit}-${line.credit}`}>{line.code} {line.name}: debit {line.debit}, credit {line.credit}</li>)}</ul>
                </li>
              ))}
            </ul>
          </section>
          <section className="panel p-4">
            <h2 className="display text-2xl font-bold">Client receipts</h2>
            <div className="mt-3"><RecordReceipt invoices={books.open_invoices} /></div>
            <ul className="mt-4 text-sm">
              {books.receipts.map((receipt) => <li key={receipt.reference}>{receipt.received_on} · {receipt.reference} · {receipt.client_name} · GHS {receipt.amount}</li>)}
            </ul>
          </section>
          <section className="panel p-4">
            <h2 className="display text-2xl font-bold">Trial balance</h2>
            <p className="mt-1 text-sm">{books.trial_balance.balanced ? "Debits equal credits." : "The trial balance is out of balance."}</p>
            <div className="sheet mt-3">
              <table className="min-w-full text-left text-sm">
                <thead className="border-b border-[var(--line)] text-[var(--muted)]"><tr><th className="px-3 py-2">Account</th><th className="px-3 py-2">Debit</th><th className="px-3 py-2">Credit</th></tr></thead>
                <tbody>
                  {books.trial_balance.rows.map((row) => (
                    <tr key={row.code} className="border-b border-[var(--line)]"><td className="px-3 py-2">{row.code} {row.name}</td><td className="px-3 py-2">{row.debit}</td><td className="px-3 py-2">{row.credit}</td></tr>
                  ))}
                  <tr><td className="px-3 py-2 font-semibold">Total</td><td className="px-3 py-2 font-semibold">{books.trial_balance.total_debit}</td><td className="px-3 py-2 font-semibold">{books.trial_balance.total_credit}</td></tr>
                </tbody>
              </table>
            </div>
            <h3 className="mt-4 font-semibold">Receivables aging</h3>
            <ul className="mt-2 text-sm">
              {books.aging.length === 0 ? <li>No outstanding invoices.</li> : books.aging.map((row) => <li key={row.invoice_id}>{row.client_name} · week {row.week_start} · GHS {row.outstanding} · {row.bucket}</li>)}
            </ul>
          </section>
        </div>
      )}
    </Shell>
  );
}
