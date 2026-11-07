import Link from "next/link";

import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Tax = {
  statutory_engine: string;
  net_pay: null;
  note: string;
  items: { name: string; status: string; amount: null }[];
};

export default async function TaxSettingsPage() {
  const result = await apiGet<Tax>("/settings/tax/");
  const tax = result.data;
  return (
    <Shell>
      <p className="text-sm font-semibold tracking-[0.14em] text-[var(--muted)]">TAX</p>
      <h1 className="display mt-1 text-4xl font-bold">Tax and pension</h1>
      <p className="mt-2 max-w-3xl text-sm text-[var(--muted)]">{tax?.note || result.message}</p>
      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        {(tax?.items ?? []).map((item) => (
          <article key={item.name} className="panel p-4">
            <h2 className="font-semibold">{item.name}</h2>
            <p className="mt-2 text-sm text-[var(--muted)]">Not configured</p>
            <p className="mt-1 text-sm">No amount is stored.</p>
          </article>
        ))}
      </div>
      <p className="mt-4 text-sm">Net pay: not calculated.</p>
      <Link className="mt-4 inline-flex text-sm font-semibold text-[var(--blue)]" href="/settings">Back to settings</Link>
    </Shell>
  );
}
