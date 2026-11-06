"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { readJson } from "@/lib/read-json";

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
  if (!response.ok) return body.error?.message || "The books did not change.";
  return null;
}

export function JournalActions({ entry }: { entry: { id: string; status: string; reversal: boolean; reversed: boolean } }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function run(path: string) {
    setPending(true);
    setMessage(null);
    const error = await postJson(path, {});
    setPending(false);
    setMessage(error);
    if (!error) router.refresh();
  }

  if (entry.status === "draft") {
    return (
      <div className="mt-2">
        <button type="button" disabled={pending} className="rounded-full bg-[#071426] px-3 py-1 text-sm font-semibold text-white disabled:opacity-60" onClick={() => void run(`/api/v1/accounting/journals/${entry.id}/post/`)}>Post draft</button>
        {message ? <p className="mt-1 text-sm">{message}</p> : null}
      </div>
    );
  }
  if (!entry.reversal && !entry.reversed) {
    return (
      <div className="mt-2">
        <button type="button" disabled={pending} className="rounded-full border border-[var(--line)] px-3 py-1 text-sm font-semibold disabled:opacity-60" onClick={() => void run(`/api/v1/accounting/journals/${entry.id}/reverse/`)}>Reverse</button>
        {message ? <p className="mt-1 text-sm">{message}</p> : null}
      </div>
    );
  }
  return null;
}

export function PeriodControl({ period }: { period: { id: string; name: string; starts_on: string; ends_on: string; status: string } }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const next = period.status === "open" ? "closed" : "open";

  return (
    <li className="rounded-xl bg-[var(--canvas)] px-3 py-2 text-sm">
      <p>{period.name} · {period.starts_on} to {period.ends_on} · {period.status}</p>
      <button
        type="button"
        disabled={pending}
        className="mt-2 rounded-full border border-[var(--line)] px-3 py-1 text-sm font-semibold disabled:opacity-60"
        onClick={() => {
          setPending(true);
          setMessage(null);
          void postJson(`/api/v1/accounting/periods/${period.id}/`, { status: next }).then((error) => {
            setPending(false);
            setMessage(error ?? (next === "closed" ? "Period closed. New posts in these dates will be refused." : "Period reopened."));
            if (!error) router.refresh();
          });
        }}
      >
        {next === "closed" ? "Close period" : "Reopen period"}
      </button>
      {message ? <p className="mt-1">{message}</p> : null}
    </li>
  );
}
