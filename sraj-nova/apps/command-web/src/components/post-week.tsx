"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { readJson } from "@/lib/read-json";

async function token() {
  const csrf = await fetch("/api/v1/auth/csrf/", { credentials: "include", cache: "reload" });
  const body = await readJson<{ data?: { csrf_token?: string } }>(csrf);
  return body?.data?.csrf_token ?? "";
}

export function PostWeek() {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function post() {
    setPending(true);
    setMessage(null);
    const response = await fetch("/api/v1/accounting/post-week/", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", "X-CSRFToken": await token() },
    });
    const body = await readJson<{ error?: { message: string }; data?: { posted_invoices: number } }>(response);
    setPending(false);
    if (!body) {
      setMessage("The journals were not posted. The server returned a page instead of data.");
      return;
    }
    if (!response.ok) {
      setMessage(body.error?.message || "The journals were not posted.");
      return;
    }
    setMessage(`Posted ${body.data?.posted_invoices ?? 0} invoice journals. A repeat post reverses the previous entry first.`);
    router.refresh();
  }

  return (
    <div>
      <button type="button" onClick={post} disabled={pending} className="rounded-full bg-[#0b1f33] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">
        {pending ? "Posting…" : "Post this week's invoices"}
      </button>
      {message ? <p className="mt-2 text-sm">{message}</p> : null}
    </div>
  );
}
