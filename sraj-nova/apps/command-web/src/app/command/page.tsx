import Link from "next/link";

import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Center = {
  as_of: string;
  scope: string;
  active_workforce: number;
  deployed_workers: number;
  scheduled_today: number;
  on_duty: number;
  late: number;
  absent: number;
  unfilled_shifts: number;
  pending_staffing_requests: number;
  expiring_contracts: number;
  workers_by_client: { client_id: string; client_name: string; workers: number }[];
  open_alerts: { severity: string; message: string }[];
  finance: {
    payroll_engine: string;
    billing_engine: string;
    reason: string;
    weekly_gross_payroll: string;
    agency_fee_revenue: string;
    outstanding_invoices: string;
    cash_available?: string;
  };
};

type ShiftLane = {
  id: string;
  site_name: string;
  position: string;
  worker_name: string | null;
  starts_at: string;
  ends_at: string;
  attendance: string;
  work_date: string;
  is_today: boolean;
};

function minutes(value: string) {
  const [hour, minute] = value.split(":").map(Number);
  return hour * 60 + (minute || 0);
}

function blockStyle(start: string, end: string) {
  const open = 5 * 60;
  const span = 18 * 60;
  let from = minutes(start);
  let to = minutes(end);
  if (to <= from) to += 24 * 60;
  const left = Math.max(0, ((from - open) / span) * 100);
  const width = Math.max(8, Math.min(100 - left, ((to - from) / span) * 100));
  return { left: `${left}%`, width: `${width}%` };
}
const metrics: { label: string; tone?: "alert"; value: (data: Center) => number }[] = [
  { label: "Active workforce", value: (data) => data.active_workforce },
  { label: "Deployed workers", value: (data) => data.deployed_workers },
  { label: "Scheduled today", value: (data) => data.scheduled_today },
  { label: "On duty", value: (data) => data.on_duty },
  { label: "Late", tone: "alert", value: (data) => data.late },
  { label: "Absent", tone: "alert", value: (data) => data.absent },
  { label: "Unfilled shifts", tone: "alert", value: (data) => data.unfilled_shifts },
  { label: "Pending requests", value: (data) => data.pending_staffing_requests },
  { label: "Contracts expiring in 30 days", tone: "alert", value: (data) => data.expiring_contracts },
];

export default async function CommandPage() {
  const [result, floorResult] = await Promise.all([apiGet<Center>("/command-center/"), apiGet<{ as_of: string; shifts: ShiftLane[] }>("/factory-floor/")]);
  if (result.status === 403) {
    return (
      <Shell>
        <h1 className="text-2xl font-semibold">Command center</h1>
        <p className="mt-3">{result.message}</p>
      </Shell>
    );
  }
  const data = result.data;
  if (!data) return null;
  const shifts = floorResult.data?.shifts ?? [];
  const focus = shifts.some((shift) => shift.is_today) ? floorResult.data?.as_of : shifts.at(-1)?.work_date;
  const lanes = [...new Set(shifts.filter((shift) => shift.work_date === focus).map((shift) => `${shift.site_name} · ${shift.position} · ${shift.worker_name ?? "Unfilled"}`))];
  return (
    <Shell>
      <p className="text-sm font-semibold tracking-[0.16em] text-[var(--orange)]">AGENCY COMMAND</p>
      <h1 className="display mt-1 text-4xl font-bold">Command center</h1>
      <p className="mt-2 max-w-3xl text-sm text-[var(--muted)]">
        {data.as_of} · {data.scope}. Late means a recorded arrival more than 10 minutes after the scheduled start.
      </p>
      {focus ? (
        <section className="panel mt-6 p-4">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="display text-3xl font-bold">Shift timeline</h2>
              <p className="text-sm text-[var(--muted)]">{focus === data.as_of ? "Today" : "Latest stored day this week"} · 05:00 to 23:00</p>
            </div>
            <Link className="text-sm font-semibold underline" href="/floor">Open the floor</Link>
          </div>
          <div className="mt-4 space-y-2">
            {lanes.map((lane) => {
              const [site, position, worker] = lane.split(" · ");
              const blocks = shifts.filter((shift) => shift.work_date === focus && shift.site_name === site && shift.position === position && (shift.worker_name ?? "Unfilled") === worker);
              return (
                <div key={lane} className="grid items-center gap-3 md:grid-cols-[220px_1fr]">
                  <p className="text-sm"><span className="font-semibold">{position}</span><br /><span className="text-[var(--muted)]">{site} · {worker}</span></p>
                  <div className="lane">
                    {blocks.map((shift) => (
                      <span key={shift.id} className={`block ${shift.attendance}`} style={blockStyle(shift.starts_at, shift.ends_at)}>
                        {shift.starts_at}–{shift.ends_at}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      ) : null}
      <section className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <article className="gauge"><span>On duty</span><strong>{data.on_duty}</strong></article>
        <article className="gauge hot"><span>Late</span><strong>{data.late}</strong></article>
        <article className="gauge"><span>Absent</span><strong>{data.absent}</strong></article>
        <article className="gauge hot"><span>Unfilled posts</span><strong>{data.unfilled_shifts}</strong></article>
      </section>
      <section className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.filter((metric) => !["On duty", "Late", "Absent", "Unfilled shifts"].includes(metric.label)).map((metric) => (
          <article key={metric.label} className={metric.tone === "alert" ? "metric alert" : "metric"}>
            <p className="text-sm text-[var(--muted)]">{metric.label}</p>
            <strong>{metric.value(data)}</strong>
          </article>
        ))}
      </section>
      <section className="mt-6 grid gap-4 lg:grid-cols-2">
        <article className="panel p-4">
          <h2 className="display text-xl font-bold">Workers by client</h2>
          <ul className="mt-3 space-y-3 text-sm">
            {data.workers_by_client.map((row) => {
              const peak = Math.max(...data.workers_by_client.map((item) => item.workers), 1);
              return (
                <li key={row.client_id}>
                  <div className="mb-1 flex items-center justify-between">
                    <span>{row.client_name}</span>
                    <span className="display text-2xl font-bold">{row.workers}</span>
                  </div>
                  <div className="bar" aria-hidden="true"><i style={{ width: `${(row.workers / peak) * 100}%` }} /></div>
                </li>
              );
            })}
          </ul>
        </article>
        <article className="panel p-4">
          <h2 className="display text-xl font-bold">Open operational alerts</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {data.open_alerts.map((alert) => (
              <li key={alert.message} className="rounded-xl bg-[var(--canvas)] px-3 py-2">{alert.message}</li>
            ))}
          </ul>
        </article>
      </section>
      <section className="panel mt-6 p-4">
        <h2 className="display text-xl font-bold">Payroll and billing</h2>
        <p className="mt-2 text-sm text-[var(--muted)]">{data.finance.reason}</p>
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-xl bg-[var(--canvas)] px-3 py-3"><dt className="text-[var(--muted)]">Weekly gross wages</dt><dd className="display text-2xl font-bold">GHS {data.finance.weekly_gross_payroll}</dd></div>
          <div className="rounded-xl bg-[var(--canvas)] px-3 py-3"><dt className="text-[var(--muted)]">Agency fee</dt><dd className="display text-2xl font-bold">GHS {data.finance.agency_fee_revenue}</dd></div>
          <div className="rounded-xl bg-[var(--canvas)] px-3 py-3"><dt className="text-[var(--muted)]">Outstanding invoices</dt><dd className="display text-2xl font-bold">GHS {data.finance.outstanding_invoices}</dd></div>
          <div className="rounded-xl bg-[var(--canvas)] px-3 py-3"><dt className="text-[var(--muted)]">Net pay and statutory amounts</dt><dd className="mt-1">Not calculated</dd></div>
          {"cash_available" in data.finance ? <div className="rounded-xl bg-[var(--canvas)] px-3 py-3"><dt className="text-[var(--muted)]">Recorded cash</dt><dd className="display text-2xl font-bold">GHS {data.finance.cash_available}</dd></div> : null}
        </dl>
      </section>
    </Shell>
  );
}
