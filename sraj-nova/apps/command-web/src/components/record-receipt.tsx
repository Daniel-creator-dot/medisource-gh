"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { readJson } from "@/lib/read-json";

type Invoice = { id: string; client_name: string; outstanding: string; posted: boolean };

export function RecordReceipt({ invoices }: { invoices: Invoice[] }) {
  const router = useRouter();
  const posted = invoices.filter((invoice) => invoice.posted);
  const [invoiceId, setInvoiceId] = useState(posted[0]?.id ?? "");
  const [amount, setAmount] = useState("");
  const [reference, setReference] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setPending(true);
    setMessage(null);
    const csrf = await fetch("/api/v1/auth/csrf/", { credentials: "include", cache: "reload" });
    const csrfBody = await readJson<{ data?: { csrf_token?: string } }>(csrf);
    const token = csrfBody?.data?.csrf_token ?? "";
    const response = await fetch("/api/v1/accounting/receipts/", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", "X-CSRFToken": token },
      body: JSON.stringify({ invoice_id: invoiceId, amount, reference }),
    });
    const body = await readJson<{ error?: { message: string } }>(response);
    setPending(false);
    if (!body) {
      setMessage("The receipt was not recorded. The server returned a page instead of data.");
      return;
    }
    if (!response.ok) {
      setMessage(body.error?.message || "The receipt was not recorded.");
      return;
    }
    setAmount("");
    setReference("");
    setMessage("Receipt recorded in the ledger. This is not a bank settlement.");
    router.refresh();
  }

  if (posted.length === 0) {
    return <p className="text-sm text-[var(--muted)]">Post the week's invoices before recording a receipt.</p>;
  }

  return (
    <form className="grid gap-3 sm:grid-cols-4" onSubmit={submit}>
      <label className="text-sm">
        Invoice
        <select className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" value={invoiceId} onChange={(event) => setInvoiceId(event.target.value)}>
          {posted.map((invoice) => (
            <option key={invoice.id} value={invoice.id}>{invoice.client_name} · GHS {invoice.outstanding}</option>
          ))}
        </select>
      </label>
      <label className="text-sm">
        Amount
        <input className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" value={amount} onChange={(event) => setAmount(event.target.value)} inputMode="decimal" required />
      </label>
      <label className="text-sm">
        Reference
        <input className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" value={reference} onChange={(event) => setReference(event.target.value)} required />
      </label>
      <div className="flex items-end">
        <button type="submit" disabled={pending} className="rounded-full bg-[var(--orange)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">
          {pending ? "Recording…" : "Record receipt"}
        </button>
      </div>
      {message ? <p className="text-sm sm:col-span-4">{message}</p> : null}
    </form>
  );
}
