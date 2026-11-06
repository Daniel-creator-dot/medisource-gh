"use client";

import { useMemo, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";

import { readJson } from "@/lib/read-json";

type Department = { id: string; name: string };
type Site = { id: string; client_id: string; client_name: string; name: string; city: string; departments: Department[] };
type Position = { id: string; client_id: string; title: string; required_skill: string };
type Worker = { id: string; number: string; name: string };

export type WorkOptions = {
  can_open_shift: boolean;
  can_record_attendance: boolean;
  can_request_staff: boolean;
  sites: Site[];
  positions: Position[];
  workers: Worker[];
};

async function post(path: string, payload: unknown) {
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
  if (!response.ok) return body.error?.message || "The action was not saved.";
  return null;
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block text-sm">
      {label}
      <span className="mt-1 block">{children}</span>
    </label>
  );
}

const control = "w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2";

export function WorkDesk({ options }: { options: WorkOptions }) {
  const router = useRouter();
  const [siteId, setSiteId] = useState(options.sites[0]?.id ?? "");
  const site = options.sites.find((item) => item.id === siteId) ?? options.sites[0];
  const positions = useMemo(
    () => options.positions.filter((position) => position.client_id === site?.client_id),
    [options.positions, site?.client_id],
  );
  const [departmentId, setDepartmentId] = useState(site?.departments[0]?.id ?? "");
  const [positionId, setPositionId] = useState(positions[0]?.id ?? "");
  const [workDate, setWorkDate] = useState("");
  const [startsAt, setStartsAt] = useState("06:00");
  const [endsAt, setEndsAt] = useState("14:00");
  const [employeeId, setEmployeeId] = useState("");
  const [punchFor, setPunchFor] = useState(options.workers[0]?.id ?? "");
  const [eventType, setEventType] = useState("in");
  const [title, setTitle] = useState("");
  const [headcount, setHeadcount] = useState("1");
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  function chooseSite(next: string) {
    const chosen = options.sites.find((item) => item.id === next);
    setSiteId(next);
    setDepartmentId(chosen?.departments[0]?.id ?? "");
    const nextPositions = options.positions.filter((position) => position.client_id === chosen?.client_id);
    setPositionId(nextPositions[0]?.id ?? "");
  }

  async function run(action: () => Promise<string | null>, success: string) {
    setPending(true);
    setMessage(null);
    const error = await action();
    setPending(false);
    setMessage(error ?? success);
    if (!error) router.refresh();
  }

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {options.can_open_shift ? (
        <form
          className="panel space-y-3 p-4"
          onSubmit={(event) => {
            event.preventDefault();
            void run(
              () => post("/api/v1/shifts/", { site_id: siteId, department_id: departmentId, position_id: positionId, work_date: workDate, starts_at: startsAt, ends_at: endsAt, employee_id: employeeId || null }),
              "Post saved. Open Coverage to place a recommended worker, or it is already filled.",
            );
          }}
        >
          <h2 className="display text-2xl font-bold">Open a post</h2>
          <Field label="Factory">
            <select className={control} value={siteId} onChange={(event) => chooseSite(event.target.value)}>
              {options.sites.map((item) => <option key={item.id} value={item.id}>{item.client_name} · {item.name}</option>)}
            </select>
          </Field>
          <Field label="Department">
            <select className={control} value={departmentId} onChange={(event) => setDepartmentId(event.target.value)}>
              {(site?.departments ?? []).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </Field>
          <Field label="Position">
            <select className={control} value={positionId} onChange={(event) => setPositionId(event.target.value)}>
              {positions.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}
            </select>
          </Field>
          <Field label="Date"><input className={control} type="date" required value={workDate} onChange={(event) => setWorkDate(event.target.value)} /></Field>
          <div className="grid grid-cols-2 gap-2">
            <Field label="Start"><input className={control} type="time" required value={startsAt} onChange={(event) => setStartsAt(event.target.value)} /></Field>
            <Field label="End"><input className={control} type="time" required value={endsAt} onChange={(event) => setEndsAt(event.target.value)} /></Field>
          </div>
          <Field label="Worker, if already chosen">
            <select className={control} value={employeeId} onChange={(event) => setEmployeeId(event.target.value)}>
              <option value="">Leave unfilled</option>
              {options.workers.map((worker) => <option key={worker.id} value={worker.id}>{worker.number} {worker.name}</option>)}
            </select>
          </Field>
          <button className="rounded-full bg-[var(--orange)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60" disabled={pending} type="submit">Save post</button>
        </form>
      ) : null}
      {options.can_record_attendance ? (
        <form
          className="panel space-y-3 p-4"
          onSubmit={(event) => {
            event.preventDefault();
            void run(
              () => post("/api/v1/attendance/", { employee_id: punchFor, event_type: eventType }),
              eventType === "in" ? "Arrival saved. The first arrival of the day is the one the floor uses." : "Departure saved.",
            );
          }}
        >
          <h2 className="display text-2xl font-bold">Record a punch</h2>
          <p className="text-sm text-[var(--muted)]">This writes a new attendance event. It does not erase an earlier punch.</p>
          {options.workers.length > 1 ? (
            <Field label="Worker">
              <select className={control} value={punchFor} onChange={(event) => setPunchFor(event.target.value)}>
                {options.workers.map((worker) => <option key={worker.id} value={worker.id}>{worker.number} {worker.name}</option>)}
              </select>
            </Field>
          ) : <p className="text-sm font-semibold">{options.workers[0] ? `${options.workers[0].number} ${options.workers[0].name}` : "No worker is linked to this login."}</p>}
          <Field label="Event">
            <select className={control} value={eventType} onChange={(event) => setEventType(event.target.value)}>
              <option value="in">Arrival</option>
              <option value="out">Departure</option>
            </select>
          </Field>
          <button className="rounded-full bg-[#16130f] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60" disabled={pending || options.workers.length === 0} type="submit">Save punch</button>
        </form>
      ) : null}
      {options.can_request_staff ? (
        <form
          className="panel space-y-3 p-4"
          onSubmit={(event) => {
            event.preventDefault();
            void run(
              () => post("/api/v1/staffing-requests/", { site_id: siteId, title, headcount }),
              "Request saved as pending.",
            );
          }}
        >
          <h2 className="display text-2xl font-bold">Request workers</h2>
          <Field label="Factory">
            <select className={control} value={siteId} onChange={(event) => chooseSite(event.target.value)}>
              {options.sites.map((item) => <option key={item.id} value={item.id}>{item.name} · {item.city}</option>)}
            </select>
          </Field>
          <Field label="What the factory needs"><input className={control} required value={title} onChange={(event) => setTitle(event.target.value)} /></Field>
          <Field label="How many"><input className={control} required inputMode="numeric" min={1} value={headcount} onChange={(event) => setHeadcount(event.target.value)} /></Field>
          <button className="rounded-full bg-[#16130f] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60" disabled={pending} type="submit">Save request</button>
        </form>
      ) : null}
      {message ? <p className="text-sm lg:col-span-3">{message}</p> : null}
    </div>
  );
}
