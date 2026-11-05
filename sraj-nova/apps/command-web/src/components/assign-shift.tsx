"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function AssignShift({ shiftId, employeeId, name }: { shiftId: string; employeeId: string; name: string }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function assign() {
    setPending(true);
    setMessage(null);
    const csrf = await fetch("/api/v1/auth/csrf/", { credentials: "include", cache: "reload" });
    const token = ((await csrf.json()) as { data: { csrf_token: string } }).data.csrf_token;
    const response = await fetch(`/api/v1/shifts/${shiftId}/assign/`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", "X-CSRFToken": token },
      body: JSON.stringify({ employee_id: employeeId }),
    });
    const body = (await response.json()) as { error?: { message: string } };
    setPending(false);
    if (!response.ok) {
      setMessage(body.error?.message || "The assignment was not saved.");
      return;
    }
    router.refresh();
  }

  return (
    <div className="mt-2">
      <button type="button" onClick={assign} disabled={pending} className="rounded-full bg-[var(--orange)] px-3 py-1 text-sm font-semibold text-white disabled:opacity-60">
        {pending ? "Assigning…" : `Assign ${name}`}
      </button>
      {message ? <p className="mt-1 text-sm text-red-700">{message}</p> : null}
    </div>
  );
}
