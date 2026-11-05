"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function RebuildWorksheet() {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function rebuild() {
    setPending(true);
    const csrf = await fetch("/api/v1/auth/csrf/", { credentials: "include", cache: "reload" });
    const token = ((await csrf.json()) as { data: { csrf_token: string } }).data.csrf_token;
    const response = await fetch("/api/v1/finance/worksheets/rebuild/", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", "X-CSRFToken": token },
    });
    setPending(false);
    if (!response.ok) {
      setMessage("The worksheet was not rebuilt.");
      return;
    }
    router.refresh();
  }

  return (
    <div className="mt-4">
      <button type="button" onClick={rebuild} disabled={pending} className="rounded-full bg-[#0b1f33] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">
        {pending ? "Rebuilding…" : "Rebuild this week's worksheet"}
      </button>
      {message ? <p className="mt-2 text-sm text-red-700">{message}</p> : null}
    </div>
  );
}
