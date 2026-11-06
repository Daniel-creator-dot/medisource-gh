"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

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
  if (!response.ok) return body.error?.message || "That change was not saved.";
  return null;
}

const control = "mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2";

export function PasswordForm() {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    const error = await postJson("/api/v1/auth/password/", { current_password: current, new_password: next });
    setPending(false);
    setMessage(error ?? "Password saved.");
    if (!error) {
      setCurrent("");
      setNext("");
    }
  }

  return (
    <form className="mt-3 space-y-3" onSubmit={(event) => void submit(event)}>
      <label className="block text-sm font-medium">
        Current password
        <input className={control} type="password" value={current} onChange={(event) => setCurrent(event.target.value)} autoComplete="current-password" />
      </label>
      <label className="block text-sm font-medium">
        New password
        <input className={control} type="password" value={next} onChange={(event) => setNext(event.target.value)} autoComplete="new-password" />
      </label>
      <button type="submit" disabled={pending} className="rounded-full bg-[var(--blue)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">
        {pending ? "Saving…" : "Save password"}
      </button>
      {message ? <p className="text-sm">{message}</p> : null}
    </form>
  );
}

export function SignOutButton() {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  async function signOut() {
    setPending(true);
    await postJson("/api/v1/auth/logout/", {});
    router.push("/");
    router.refresh();
  }

  return (
    <button type="button" disabled={pending} className="rounded-full border border-[var(--line)] px-4 py-2 text-sm font-semibold disabled:opacity-60" onClick={() => void signOut()}>
      {pending ? "Signing out…" : "Sign out"}
    </button>
  );
}

export function RoleForm({ userId, role, choices }: { userId: string; role: string; choices: { value: string; label: string }[] }) {
  const router = useRouter();
  const [value, setValue] = useState(role);
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function save() {
    setPending(true);
    const error = await postJson(`/api/v1/auth/users/${userId}/role/`, { role: value });
    setPending(false);
    setMessage(error);
    if (!error) router.refresh();
  }

  if (choices.length < 2) return <span>{choices[0]?.label ?? role}</span>;
  return (
    <div className="flex flex-wrap items-center gap-2">
      <select className="rounded-xl border border-[var(--line)] bg-white px-2 py-1" value={value} onChange={(event) => setValue(event.target.value)}>
        {choices.map((choice) => (
          <option key={choice.value} value={choice.value}>{choice.label}</option>
        ))}
      </select>
      <button type="button" disabled={pending || value === role} className="rounded-full bg-[var(--blue)] px-3 py-1 text-sm font-semibold text-white disabled:opacity-60" onClick={() => void save()}>
        Save
      </button>
      {message ? <span className="text-sm">{message}</span> : null}
    </div>
  );
}
