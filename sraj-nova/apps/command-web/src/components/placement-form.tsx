"use client";

import { useEffect, useState, type FormEvent } from "react";

import { readJson } from "@/lib/read-json";

type Department = { id: string; name: string };
type Site = { id: string; client_id: string; client_name: string; name: string; departments: Department[] };
type Position = { id: string; client_id: string; title: string; required_skill: string };
type Options = { sites: Site[]; positions: Position[] };

const control = "mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2";

async function postJson(path: string, payload: unknown) {
  const csrf = await fetch("/api/v1/auth/csrf/", { credentials: "include", cache: "reload" });
  const csrfBody = await readJson<{ data?: { csrf_token?: string } }>(csrf);
  const response = await fetch(path, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrfBody?.data?.csrf_token ?? "" },
    body: JSON.stringify(payload),
  });
  const body = await readJson<{ data?: { agency_employee_number?: string; name?: string }; error?: { message: string } }>(response);
  if (!body) return { error: "The server returned a page instead of data." };
  if (!response.ok) return { error: body.error?.message || "That was not saved." };
  return { error: null, data: body.data };
}

export function usePlacementOptions() {
  const [options, setOptions] = useState<Options | null>(null);
  const [siteId, setSiteId] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [positionId, setPositionId] = useState("");
  const [skill, setSkill] = useState("");

  useEffect(() => {
    void fetch("/api/v1/work/options/", { credentials: "include" })
      .then((response) => readJson<{ data?: Options }>(response))
      .then((body) => {
        const data = body?.data;
        if (!data) return;
        setOptions(data);
        const site = data.sites[0];
        const position = data.positions.find((item) => item.client_id === site?.client_id);
        setSiteId(site?.id ?? "");
        setDepartmentId(site?.departments[0]?.id ?? "");
        setPositionId(position?.id ?? "");
        setSkill(position?.required_skill ?? "");
      });
  }, []);

  const site = options?.sites.find((item) => item.id === siteId);
  const positions = (options?.positions ?? []).filter((item) => item.client_id === site?.client_id);

  function chooseSite(next: string) {
    const chosen = options?.sites.find((item) => item.id === next);
    const position = options?.positions.find((item) => item.client_id === chosen?.client_id);
    setSiteId(next);
    setDepartmentId(chosen?.departments[0]?.id ?? "");
    setPositionId(position?.id ?? "");
    setSkill(position?.required_skill ?? "");
  }

  function choosePosition(next: string) {
    const position = positions.find((item) => item.id === next);
    setPositionId(next);
    if (position?.required_skill) setSkill(position.required_skill);
  }

  return { options, site, positions, siteId, departmentId, positionId, skill, setDepartmentId, setSkill, chooseSite, choosePosition };
}

export function PlacementFields(props: ReturnType<typeof usePlacementOptions>) {
  const { options, site, positions, siteId, departmentId, positionId, skill, setDepartmentId, setSkill, chooseSite, choosePosition } = props;
  if (!options) return <p className="text-sm text-[var(--muted)]">Loading plants…</p>;
  return (
    <>
      <label className="block text-sm font-medium">
        Plant
        <select className={control} value={siteId} onChange={(event) => chooseSite(event.target.value)}>
          {options.sites.map((item) => <option key={item.id} value={item.id}>{item.name} · {item.client_name}</option>)}
        </select>
      </label>
      <label className="block text-sm font-medium">
        Department
        <select className={control} value={departmentId} onChange={(event) => setDepartmentId(event.target.value)}>
          {(site?.departments ?? []).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </label>
      <label className="block text-sm font-medium">
        Position
        <select className={control} value={positionId} onChange={(event) => choosePosition(event.target.value)}>
          {positions.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}
        </select>
      </label>
      <label className="block text-sm font-medium">
        Skill
        <input className={control} value={skill} onChange={(event) => setSkill(event.target.value)} />
      </label>
    </>
  );
}

export function HrDesk() {
  const placement = usePlacementOptions();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [rate, setRate] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    const result = await postJson("/api/v1/hr/staff/", {
      first_name: firstName,
      last_name: lastName,
      site_id: placement.siteId,
      department_id: placement.departmentId,
      position_id: placement.positionId,
      hourly_rate: rate,
      skill: placement.skill,
    });
    setPending(false);
    if (result.error) {
      setMessage(result.error);
      return;
    }
    setMessage(`${result.data?.agency_employee_number} ${result.data?.name} is on the staff list.`);
    setFirstName("");
    setLastName("");
    setRate("");
  }

  return (
    <form className="panel space-y-3 p-5" onSubmit={(event) => void submit(event)}>
      <h2 className="text-lg font-semibold">Add staff</h2>
      <p className="text-sm text-[var(--muted)]">The worker is placed in the department you choose. This stores the record and the hourly rate. It does not create a sign-in, and it does not calculate PAYE or pension.</p>
      <label className="block text-sm font-medium">First name<input className={control} value={firstName} onChange={(event) => setFirstName(event.target.value)} /></label>
      <label className="block text-sm font-medium">Last name<input className={control} value={lastName} onChange={(event) => setLastName(event.target.value)} /></label>
      <PlacementFields {...placement} />
      <label className="block text-sm font-medium">Hourly rate (GHS)<input className={control} inputMode="decimal" value={rate} onChange={(event) => setRate(event.target.value)} /></label>
      <button type="submit" disabled={pending} className="rounded-full bg-[var(--blue)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">{pending ? "Saving…" : "Add to staff"}</button>
      {message ? <p className="text-sm">{message}</p> : null}
    </form>
  );
}

type Applicant = {
  id: string;
  first_name: string;
  last_name: string;
  phone: string;
  skill: string;
  status: string;
  note: string;
  is_demo: boolean;
  site_name: string;
  department: string;
  position: string;
  employee_number: string | null;
};

export function RecruitmentDesk({ applicants }: { applicants: Applicant[] }) {
  const placement = usePlacementOptions();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [note, setNote] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [rates, setRates] = useState<Record<string, string>>({});

  async function add(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    const result = await postJson("/api/v1/hr/applicants/", {
      first_name: firstName,
      last_name: lastName,
      phone,
      note,
      skill: placement.skill,
      site_id: placement.siteId,
      department_id: placement.departmentId,
      position_id: placement.positionId,
    });
    setPending(false);
    setMessage(result.error ?? "Application stored.");
    if (!result.error) window.location.reload();
  }

  async function setStatus(id: string, status: string) {
    const result = await postJson(`/api/v1/hr/applicants/${id}/status/`, { status });
    setMessage(result.error ?? "Status stored.");
    if (!result.error) window.location.reload();
  }

  async function hire(id: string) {
    const result = await postJson(`/api/v1/hr/applicants/${id}/hire/`, { hourly_rate: rates[id] || "" });
    setMessage(result.error ?? `${result.data?.agency_employee_number} ${result.data?.name} is now on the staff list.`);
    if (!result.error) window.location.reload();
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[360px_1fr]">
      <form className="panel space-y-3 p-5" onSubmit={(event) => void add(event)}>
        <h2 className="text-lg font-semibold">New application</h2>
        <label className="block text-sm font-medium">First name<input className={control} value={firstName} onChange={(event) => setFirstName(event.target.value)} /></label>
        <label className="block text-sm font-medium">Last name<input className={control} value={lastName} onChange={(event) => setLastName(event.target.value)} /></label>
        <label className="block text-sm font-medium">Phone<input className={control} value={phone} onChange={(event) => setPhone(event.target.value)} /></label>
        <PlacementFields {...placement} />
        <label className="block text-sm font-medium">Note<input className={control} value={note} onChange={(event) => setNote(event.target.value)} /></label>
        <button type="submit" disabled={pending} className="rounded-full bg-[var(--blue)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">{pending ? "Saving…" : "Save application"}</button>
        {message ? <p className="text-sm">{message}</p> : null}
      </form>
      <div className="space-y-3">
        {applicants.length === 0 ? <p className="panel p-4 text-sm">No application is stored.</p> : null}
        {applicants.map((applicant) => (
          <article key={applicant.id} className="panel p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">{applicant.first_name} {applicant.last_name}</h2>
                <p className="text-sm text-[var(--muted)]">{applicant.position} · {applicant.department} · {applicant.site_name}</p>
                <p className="mt-1 text-sm capitalize">{applicant.status}{applicant.is_demo ? " · sample application" : ""}{applicant.phone ? ` · ${applicant.phone}` : ""}</p>
                {applicant.note ? <p className="mt-1 text-sm">{applicant.note}</p> : null}
                {applicant.employee_number ? <p className="mt-1 text-sm">Staff number {applicant.employee_number}</p> : null}
              </div>
              {applicant.status !== "hired" && applicant.status !== "rejected" ? (
                <div className="flex flex-wrap gap-2">
                  <button type="button" className="rounded-full border border-[var(--line)] px-3 py-1 text-sm" onClick={() => void setStatus(applicant.id, "screening")}>Screening</button>
                  <button type="button" className="rounded-full border border-[var(--line)] px-3 py-1 text-sm" onClick={() => void setStatus(applicant.id, "offered")}>Offer</button>
                  <button type="button" className="rounded-full border border-[var(--line)] px-3 py-1 text-sm" onClick={() => void setStatus(applicant.id, "rejected")}>Reject</button>
                </div>
              ) : null}
            </div>
            {applicant.status !== "hired" && applicant.status !== "rejected" ? (
              <div className="mt-3 flex flex-wrap items-end gap-2">
                <label className="text-sm font-medium">
                  Hourly rate (GHS)
                  <input className={control} inputMode="decimal" value={rates[applicant.id] ?? ""} onChange={(event) => setRates({ ...rates, [applicant.id]: event.target.value })} />
                </label>
                <button type="button" className="rounded-full bg-[var(--blue)] px-4 py-2 text-sm font-semibold text-white" onClick={() => void hire(applicant.id)}>Hire into department</button>
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </div>
  );
}
