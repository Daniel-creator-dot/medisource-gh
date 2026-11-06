"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { readJson } from "@/lib/read-json";

export function ClockPunch({ employeeId }: { employeeId: string }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function punch(eventType: "in" | "out") {
    setPending(true);
    setMessage(null);
    const csrf = await fetch("/api/v1/auth/csrf/", { credentials: "include", cache: "reload" });
    const csrfBody = await readJson<{ data?: { csrf_token?: string } }>(csrf);
    const response = await fetch("/api/v1/attendance/", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrfBody?.data?.csrf_token ?? "" },
      body: JSON.stringify({ employee_id: employeeId, event_type: eventType }),
    });
    const body = await readJson<{ error?: { message: string } }>(response);
    setPending(false);
    if (!body || !response.ok) {
      setMessage(body?.error?.message || "The punch was not saved.");
      return;
    }
    setMessage(eventType === "in" ? "Arrival saved." : "Departure saved.");
    router.refresh();
  }

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <button type="button" disabled={pending} onClick={() => void punch("in")} className="rounded-full bg-[#16130f] px-3 py-1 text-sm font-semibold text-white disabled:opacity-60">Arrival</button>
      <button type="button" disabled={pending} onClick={() => void punch("out")} className="rounded-full border border-[var(--line)] px-3 py-1 text-sm font-semibold disabled:opacity-60">Departure</button>
      {message ? <span className="text-sm">{message}</span> : null}
    </div>
  );
}
