"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { readJson } from "@/lib/read-json";

type Account = { code: string; name: string };
type Line = { code: string; debit: string; credit: string };

async function postJson(path: string, payload: unknown) {
  const csrf = await fetch("/api/v1/auth/csrf/", { credentials: "include", cache: "reload" });
  const csrfBody = await readJson<{ data?: { csrf_token?: string } }>(csrf);
  const response = await fetch(path, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrfBody?.data?.csrf_token ?? "" },
    body: JSON.stringify(payload),
  });
  const body = await readJson<{ error?: { message: string } }>(response);
  if (!body) return "The server returned a page instead of data.";
  if (!response.ok) return body.error?.message || "The journal was not saved.";
  return null;
}

export function ManualJournal({ accounts }: { accounts: Account[] }) {
  const router = useRouter();
  const first = accounts[0]?.code ?? "";
  const [memo, setMemo] = useState("");
  const [entryDate, setEntryDate] = useState("");
  const [lines, setLines] = useState<Line[]>([
    { code: first, debit: "", credit: "" },
    { code: first, debit: "", credit: "" },
  ]);
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  function update(index: number, patch: Partial<Line>) {
    setLines((current) => current.map((line, lineIndex) => (lineIndex === index ? { ...line, ...patch } : line)));
  }

  return (
    <form
      className="mt-3 space-y-3"
      onSubmit={(event) => {
        event.preventDefault();
        setPending(true);
        setMessage(null);
        void postJson("/api/v1/accounting/journals/", {
          entry_date: entryDate,
          memo,
          lines: lines.map((line) => ({ code: line.code, debit: line.debit || "0", credit: line.credit || "0" })),
        }).then((error) => {
          setPending(false);
          setMessage(error ?? "Draft saved. It is not in the trial balance until you post it.");
          if (!error) router.refresh();
        });
      }}
    >
      <p className="text-sm text-[var(--muted)]">A draft can be unbalanced. Posting refuses it until the debits equal the credits. A posted journal is not edited.</p>
      <div className="grid gap-2 sm:grid-cols-2">
        <label className="text-sm">Date<input className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" required type="date" value={entryDate} onChange={(event) => setEntryDate(event.target.value)} /></label>
        <label className="text-sm">Memo<input className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" required value={memo} onChange={(event) => setMemo(event.target.value)} /></label>
      </div>
      {lines.map((line, index) => (
        <div key={index} className="grid gap-2 sm:grid-cols-[1.4fr_0.8fr_0.8fr]">
          <label className="text-sm">Account
            <select className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" value={line.code} onChange={(event) => update(index, { code: event.target.value })}>
              {accounts.map((account) => <option key={account.code} value={account.code}>{account.code} {account.name}</option>)}
            </select>
          </label>
          <label className="text-sm">Debit<input className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" inputMode="decimal" value={line.debit} onChange={(event) => update(index, { debit: event.target.value })} /></label>
          <label className="text-sm">Credit<input className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" inputMode="decimal" value={line.credit} onChange={(event) => update(index, { credit: event.target.value })} /></label>
        </div>
      ))}
      <div className="flex flex-wrap gap-2">
        <button type="button" className="rounded-full border border-[var(--line)] px-4 py-2 text-sm font-semibold" onClick={() => setLines((current) => [...current, { code: first, debit: "", credit: "" }])}>Add line</button>
        <button type="submit" disabled={pending} className="rounded-full bg-[var(--orange)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">Save draft</button>
      </div>
      {message ? <p className="text-sm">{message}</p> : null}
    </form>
  );
}
