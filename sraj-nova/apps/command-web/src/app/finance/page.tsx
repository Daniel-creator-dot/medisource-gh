import { RebuildWorksheet } from "@/components/rebuild-worksheet";
import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Finance = {
  week_start: string;
  currency: string;
  weekly_gross_payroll: string;
  agency_fee: string;
  outstanding_invoices: string;
  estimated_net_payroll: string | null;
  statutory_liabilities: string | null;
  basis: string;
  cash_available?: string;
  cash_after_payroll?: string;
  cash_note?: string;
  invoices: { client_name: string; employment_cost: string; agency_fee: string; total: string; status: string; is_demo: boolean }[];
};

type Me = { role: string };

export default async function FinancePage() {
  const [result, me] = await Promise.all([apiGet<Finance>("/finance/"), apiGet<Me>("/auth/me/")]);
  const data = result.data;
  const agency = me.data?.role === "agency_owner" || me.data?.role === "agency_operations" || me.data?.role === "agency_finance";
  return (
    <Shell>
      <p className="text-sm font-semibold tracking-[0.16em] text-[var(--orange)]">FUNDING</p>
      <h1 className="display mt-1 text-4xl font-bold">Financial control center</h1>
      {result.status === 403 || !data ? (
        <p className="mt-3">{result.message || "This account cannot open the financial control center."}</p>
      ) : (
        <>
          <p className="mt-2 text-sm text-[var(--muted)]">Week starting {data.week_start}. {data.basis}</p>
          <section className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <article className="metric"><p className="text-sm text-[var(--muted)]">Weekly gross wages</p><strong>{data.currency} {data.weekly_gross_payroll}</strong></article>
            <article className="metric"><p className="text-sm text-[var(--muted)]">Agency management fee</p><strong>{data.currency} {data.agency_fee}</strong></article>
            <article className="metric alert"><p className="text-sm text-[var(--muted)]">Outstanding invoices</p><strong>{data.currency} {data.outstanding_invoices}</strong></article>
            {data.cash_available ? <article className="metric"><p className="text-sm text-[var(--muted)]">Recorded cash</p><strong>{data.currency} {data.cash_available}</strong></article> : null}
            {data.cash_after_payroll ? <article className="metric"><p className="text-sm text-[var(--muted)]">Cash after gross wages</p><strong>{data.currency} {data.cash_after_payroll}</strong></article> : null}
            <article className="panel p-4"><p className="text-sm text-[var(--muted)]">Net pay and statutory liabilities</p><p className="mt-2 text-sm">Not calculated. A qualified Ghana payroll review is required before those amounts exist.</p></article>
          </section>
          {data.cash_note ? <p className="mt-4 text-sm">{data.cash_note}</p> : null}
          <div className="sheet mt-4">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-[var(--line)] text-[var(--muted)]">
                <tr>
                  <th className="px-3 py-2 font-medium">Client</th>
                  <th className="px-3 py-2 font-medium">Employment cost</th>
                  <th className="px-3 py-2 font-medium">Agency fee</th>
                  <th className="px-3 py-2 font-medium">Invoice total</th>
                </tr>
              </thead>
              <tbody>
                {data.invoices.map((invoice) => (
                  <tr key={invoice.client_name} className="border-b border-[var(--line)]">
                    <td className="px-3 py-2">{invoice.client_name}{invoice.is_demo ? " · sample" : ""}</td>
                    <td className="px-3 py-2">{invoice.employment_cost}</td>
                    <td className="px-3 py-2">{invoice.agency_fee}</td>
                    <td className="px-3 py-2">{invoice.total}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {agency ? <RebuildWorksheet /> : null}
        </>
      )}
    </Shell>
  );
}
