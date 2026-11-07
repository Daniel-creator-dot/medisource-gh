import Link from "next/link";

import { ClockPunch } from "@/components/clock-punch";
import { apiGet } from "@/lib/api";

type Shift = {
  id: string;
  work_date: string;
  is_today: boolean;
  client_name: string;
  site_name: string;
  city: string;
  department: string;
  position: string;
  required_skill: string;
  skill_cover: string;
  starts_at: string;
  ends_at: string;
  hours: string;
  attendance: string;
  employee_id: string | null;
  worker_number: string | null;
  worker_name: string | null;
  hourly_rate?: string;
  labor_cost?: string;
};

type Floor = {
  as_of: string;
  week_start: string;
  shifts: Shift[];
  certifications: { employee_id: string; worker_name: string; name: string; expires_on: string; state: string }[];
  leave: { employee_id: string; worker_name: string; starts_on: string; ends_on: string; status: string }[];
};

function width(hours: string) {
  const value = Math.min(100, (Number(hours) / 12) * 100);
  return Number.isFinite(value) ? value : 0;
}

export default async function FloorPage() {
  const [result, me] = await Promise.all([
    apiGet<Floor>("/factory-floor/"),
    apiGet<{ role: string }>("/auth/me/"),
  ]);
  const floor = result.data;
  if (result.status === 403 || !floor) {
    return (
      <>
        <h1 className="display text-4xl font-bold">Factory floor</h1>
        <p className="mt-3">{result.message || "This account cannot open the factory floor."}</p>
      </>
    );
  }
  const canPunch = me.data?.role !== "client_user";
  const sites = [...new Set(floor.shifts.map((shift) => `${shift.client_name} · ${shift.site_name}`))];
  return (
    <>
      <p className="text-sm font-semibold tracking-[0.16em] text-[var(--orange)]">LIVE SHIFT BOARD</p>
      <h1 className="display mt-1 text-4xl font-bold">Factory floor</h1>
      <p className="mt-2 max-w-3xl text-sm text-[var(--muted)]">
        Week starting {floor.week_start}. Today is {floor.as_of}. A late mark is an arrival more than 10 minutes after the scheduled start. Skill cover compares the position skill with the worker&apos;s recorded qualifications.
      </p>
      <section className="mt-6 grid gap-4 xl:grid-cols-[1.7fr_0.8fr]">
        <div className="space-y-5">
          {[...new Set(floor.shifts.map((shift) => shift.work_date))].map((date) => (
            <section key={date} className="space-y-3">
              <h2 className="display text-3xl font-bold">{date === floor.as_of ? `Today · ${date}` : date}</h2>
              {sites.filter((site) => floor.shifts.some((shift) => shift.work_date === date && `${shift.client_name} · ${shift.site_name}` === site)).map((site) => (
              <section key={`${date}-${site}`} className="panel p-4">
              <h3 className="display text-2xl font-bold">{site}</h3>
              {[...new Set(floor.shifts.filter((shift) => shift.work_date === date && `${shift.client_name} · ${shift.site_name}` === site).map((shift) => shift.department))].map((department) => (
              <div key={department} className="mt-4">
              <h4 className="text-sm font-semibold tracking-[0.12em] text-[var(--muted)]">{department.toUpperCase()}</h4>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                {floor.shifts.filter((shift) => shift.work_date === date && `${shift.client_name} · ${shift.site_name}` === site && shift.department === department).map((shift) => (
                  <article key={shift.id} className={`shift ${shift.attendance} ${shift.skill_cover === "gap" ? "gap" : ""}`}>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="display text-xl font-bold">{shift.position}</p>
                        <p className="text-sm text-[var(--muted)]">{shift.department} · {shift.city}</p>
                      </div>
                      <span className="pill">{shift.attendance.replace("_", " ")}</span>
                    </div>
                    <p className="mt-3 text-sm">
                      {shift.worker_name ? (
                        <Link className="font-semibold underline" href={`/employees/${shift.employee_id}`}>{shift.worker_number} {shift.worker_name}</Link>
                      ) : "Unfilled post"}
                    </p>
                    <p className="mt-1 text-sm text-[var(--muted)]">{shift.starts_at}–{shift.ends_at} · {shift.hours} h{shift.hourly_rate ? ` · GHS ${shift.hourly_rate}/h · GHS ${shift.labor_cost}` : ""}</p>
                    <div className="bar mt-3" aria-hidden="true"><i style={{ width: `${width(shift.hours)}%` }} /></div>
                    {canPunch && shift.is_today && shift.employee_id ? <ClockPunch employeeId={shift.employee_id} /> : null}
                    <p className="mt-2 text-xs uppercase tracking-[0.08em] text-[var(--muted)]">
                      {shift.required_skill ? `${shift.required_skill} · ${shift.skill_cover.replace("_", " ")}` : "No skill requirement stored"}
                    </p>
                  </article>
                ))}
              </div>
              </div>
              ))}
            </section>
              ))}
            </section>
          ))}
        </div>
        <aside className="space-y-4">
          <section className="panel p-4">
            <h2 className="display text-2xl font-bold">On leave today</h2>
            <ul className="mt-3 space-y-2 text-sm">
              {floor.leave.length === 0 ? <li>No approved leave overlaps today.</li> : floor.leave.map((item) => (
                <li key={`${item.employee_id}-${item.starts_on}`} className="rounded-xl bg-[var(--canvas)] px-3 py-2">{item.worker_name} · {item.starts_on} to {item.ends_on}</li>
              ))}
            </ul>
          </section>
          <section className="panel p-4">
            <h2 className="display text-2xl font-bold">Tickets due in 60 days</h2>
            <ul className="mt-3 space-y-2 text-sm">
              {floor.certifications.length === 0 ? <li>No stored certification expires in that window.</li> : floor.certifications.map((item) => (
                <li key={`${item.employee_id}-${item.name}`} className="rounded-xl bg-[var(--canvas)] px-3 py-2">
                  <span className="pill">{item.state}</span> {item.worker_name} · {item.name} · {item.expires_on}
                </li>
              ))}
            </ul>
          </section>
        </aside>
      </section>
    </>
  );
}
