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
  board: {
    attendance_week: { date: string; is_today: boolean; future: boolean; scheduled: number; unfilled: number; on_duty: number | null; present: number | null; late: number | null; absent: number | null }[];
    heatmap: { site: string; days: { date: string; filled: number; unfilled: number }[] }[];
    invoice_weeks: { week_start: string; employment_cost: string; agency_fee: string; outstanding: string }[];
    clients_this_week: { client_name: string; employment_cost: string; agency_fee: string; outstanding: string }[];
    unpaid_invoices: { client_name: string; week_start: string; outstanding: string }[];
    activity: { at: string; kind: string; text: string; href: string }[];
    payroll_approval_note: string;
    net_profitability: null;
    net_profitability_reason: string;
    statutory_note: string;
  };
};

type FloorSlice = {
  as_of: string;
  shifts: {
    id: string;
    site_name: string;
    position: string;
    worker_name: string | null;
    starts_at: string;
    ends_at: string;
    attendance: string;
    work_date: string;
    is_today: boolean;
  }[];
  certifications: { employee_id: string; worker_name: string; name: string; expires_on: string; state: string }[];
};

function WeekChart({ days }: { days: Center["board"]["attendance_week"] }) {
  const width = 640;
  const height = 220;
  const max = Math.max(...days.map((day) => Math.max(day.scheduled, day.unfilled)), 1);
  const x = (index: number) => 24 + (index * (width - 48)) / Math.max(days.length - 1, 1);
  const y = (value: number) => 16 + (1 - value / max) * (height - 48);
  const path = (pick: (day: Center["board"]["attendance_week"][number]) => number) =>
    days.map((day, index) => `${index === 0 ? "M" : "L"} ${x(index)} ${y(pick(day))}`).join(" ");
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="mt-4 w-full" role="img" aria-label="Filled and open posts for each day this week">
      <path d={path((day) => day.scheduled)} fill="none" stroke="#2f6bff" strokeWidth="3" />
      <path d={path((day) => day.unfilled)} fill="none" stroke="#d89a12" strokeWidth="3" />
      {days.map((day, index) => (
        <text key={day.date} x={x(index)} y={height - 6} textAnchor="middle" fontSize="12" fill="#7b8798">{day.date.slice(5)}</text>
      ))}
    </svg>
  );
}

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

export default async function CommandPage() {
  const [result, floorResult] = await Promise.all([
    apiGet<Center>("/command-center/"),
    apiGet<FloorSlice>("/factory-floor/"),
  ]);
  if (result.status === 403) {
    return (
      <Shell>
        <h1 className="display text-4xl font-bold">Command center</h1>
        <p className="mt-3">{result.message}</p>
      </Shell>
    );
  }
  const data = result.data;
  if (!data) return null;
  const floor = floorResult.data;
  const shifts = floor?.shifts ?? [];
  const focus = shifts.some((shift) => shift.is_today) ? floor?.as_of : shifts.at(-1)?.work_date;
  const lanes = [...new Set(shifts.filter((shift) => shift.work_date === focus).map((shift) => `${shift.site_name} · ${shift.position} · ${shift.worker_name ?? "Unfilled"}`))];
  const peak = Math.max(...data.workers_by_client.map((item) => item.workers), 1);
  const weekMax = Math.max(...data.board.attendance_week.map((day) => day.scheduled + day.unfilled), 1);
  const wagePeak = Math.max(...data.board.invoice_weeks.map((week) => Number(week.employment_cost) + Number(week.agency_fee)), 1);
  const counts = [
    { label: "Total active employees", value: String(data.active_workforce), href: "/employees" },
    { label: "Currently deployed", value: String(data.deployed_workers), href: "/employees" },
    { label: "Scheduled today", value: String(data.scheduled_today), href: "/floor" },
    { label: "Verified on duty", value: String(data.on_duty), href: "/floor" },
  ];
  const money = [
    { label: "Weekly gross wages", value: `GHS ${data.finance.weekly_gross_payroll}`, href: "/finance", missing: false },
    { label: "Upcoming salary payment", value: "Not scheduled", href: "/finance", missing: true },
    { label: "Client receivables", value: `GHS ${data.finance.outstanding_invoices}`, href: "/finance", missing: false },
    { label: "Available cash", value: data.finance.cash_available ? `GHS ${data.finance.cash_available}` : "Not in this sign-in", href: "/accounting", missing: !data.finance.cash_available },
    { label: "Agency fee revenue", value: `GHS ${data.finance.agency_fee_revenue}`, href: "/finance", missing: false },
    { label: "Net profitability", value: "Not calculated", href: "/accounting", missing: true },
  ];

  return (
    <Shell>
      <div className="dash">
        <div className="space-y-4">
          <section className="grid gap-3 sm:grid-cols-3">
            {money.filter((item) => !item.missing).slice(0, 3).map((item) => (
              <Link key={item.label} href={item.href} className={item.missing ? "metric alert" : "metric"}>
                <p className="text-sm text-[var(--muted)]">{item.label}</p>
                <strong>{item.value}</strong>
              </Link>
            ))}
          </section>
          <article className="panel p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Workforce this week</h2>
                <p className="text-sm text-[var(--muted)]">Filled posts and open posts from stored shifts. {data.as_of}.</p>
              </div>
              <Link className="rounded-full bg-[#eef3ff] px-3 py-1 text-sm font-semibold text-[var(--blue)]" href="/floor">Floor</Link>
            </div>
            <WeekChart days={data.board.attendance_week} />
            <p className="mt-2 flex gap-4 text-sm text-[var(--muted)]"><span className="text-[var(--blue)]">Filled</span><span className="text-[#d89a12]">Open</span></p>
          </article>
          <section className="grid gap-3 sm:grid-cols-3">
            {counts.map((item) => (
              <Link key={item.label} href={item.href} className="metric">
                <p className="text-sm text-[var(--muted)]">{item.label}</p>
                <strong>{item.value}</strong>
              </Link>
            ))}
          </section>
        </div>
        <aside className="space-y-4">
          <article className="rounded-3xl bg-[var(--blue)] p-5 text-white shadow-[var(--shadow)]">
            <p className="text-sm text-white/80">Recorded cash</p>
            <p className="display mt-2 text-4xl font-bold">{data.finance.cash_available ? `GHS ${data.finance.cash_available}` : "Not in this sign-in"}</p>
            <p className="mt-3 text-sm text-white/80">Book balance only. No bank or mobile-money payment has been made.</p>
            <Link className="mt-4 inline-flex rounded-full bg-white px-4 py-2 text-sm font-semibold text-[var(--blue)]" href="/accounting">Open books</Link>
          </article>
          <article className="panel p-4">
            <h2 className="font-semibold">This week by client</h2>
            <ul className="mt-3 space-y-3 text-sm">
              {data.board.clients_this_week.length === 0 ? <li className="text-[var(--muted)]">No invoice is stored for this week.</li> : data.board.clients_this_week.map((row) => (
                <li key={row.client_name}>
                  <p className="font-semibold">{row.client_name}</p>
                  <p className="text-[var(--muted)]">Wages GHS {row.employment_cost}</p>
                  <p className="text-[var(--muted)]">Fee GHS {row.agency_fee}</p>
                </li>
              ))}
            </ul>
          </article>
          <article className="panel p-4">
            <h2 className="font-semibold">Not a profit figure</h2>
            <p className="mt-2 text-sm text-[var(--muted)]">{data.board.net_profitability_reason}</p>
            <p className="mt-2 text-sm text-[var(--muted)]">{data.board.statutory_note}</p>
          </article>
        </aside>
      </div>

      <section className="mt-6 grid gap-4 lg:grid-cols-2">
        <article className="panel p-4">
          <h2 className="display text-2xl font-bold">Deployment by client</h2>
          <p className="text-sm text-[var(--muted)]">Current deployments. This is not a forecast.</p>
          <ul className="mt-4 space-y-3 text-sm">
            {data.workers_by_client.length === 0 ? <li>No current deployments in this sign-in.</li> : data.workers_by_client.map((row) => (
              <li key={row.client_id}>
                <div className="mb-1 flex items-center justify-between">
                  <span>{row.client_name}</span>
                  <span className="display text-2xl font-bold">{row.workers}</span>
                </div>
                <div className="bar" aria-hidden="true"><i style={{ width: `${(row.workers / peak) * 100}%` }} /></div>
              </li>
            ))}
          </ul>
        </article>
        <article className="panel p-4">
          <h2 className="display text-2xl font-bold">This week&apos;s attendance</h2>
          <p className="text-sm text-[var(--muted)]">Each column is a stored shift day. A future day stays scheduled and is not marked absent.</p>
          <div className="mt-4 grid grid-cols-7 gap-2">
            {data.board.attendance_week.map((day) => (
              <div key={day.date} className="text-center text-xs">
                <div className="mx-auto flex h-28 w-full items-end justify-center rounded-xl bg-[var(--canvas)]">
                  <i className="block w-2/3 rounded-t-lg bg-[var(--blue)]" style={{ height: `${((day.scheduled + day.unfilled) / weekMax) * 100}%` }} />
                </div>
                <p className="mt-1 font-semibold">{day.date.slice(5)}</p>
                <p className="text-[var(--muted)]">{day.future ? `${day.scheduled} scheduled` : `${day.on_duty ?? 0} on duty`}</p>
                <p className="text-[var(--muted)]">{day.future ? "" : `${day.late ?? 0} late · ${day.absent ?? 0} absent`}</p>
                <p className="text-[var(--muted)]">{day.unfilled} open</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      {focus ? (
        <section className="panel mt-6 p-4">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="display text-3xl font-bold">Shift timeline</h2>
              <p className="text-sm text-[var(--muted)]">{focus === data.as_of ? "Today" : "Latest stored day this week"} · 05:00 to 23:00</p>
            </div>
            <Link className="text-sm font-semibold text-[var(--blue)]" href="/floor">Open the floor</Link>
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
                      <span key={shift.id} className={`shift-block ${shift.attendance}`} style={blockStyle(shift.starts_at, shift.ends_at)}>
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

      <section className="mt-6 grid gap-4 lg:grid-cols-2">
        <article className="panel p-4">
          <h2 className="display text-2xl font-bold">Stored invoice weeks</h2>
          <p className="text-sm text-[var(--muted)]">Wages and agency fee from issued invoices. Weeks with no invoice are omitted.</p>
          <ul className="mt-4 space-y-3 text-sm">
            {data.board.invoice_weeks.length === 0 ? <li>No invoice has been stored.</li> : data.board.invoice_weeks.map((week) => (
              <li key={week.week_start}>
                <div className="mb-1 flex justify-between"><Link href="/finance">Week {week.week_start}</Link><span>GHS {week.outstanding} outstanding</span></div>
                <div className="bar" aria-hidden="true"><i style={{ width: `${(Number(week.employment_cost) / wagePeak) * 100}%` }} /></div>
                <p className="mt-1 text-[var(--muted)]">Wages GHS {week.employment_cost} · fee GHS {week.agency_fee}</p>
              </li>
            ))}
          </ul>
        </article>
        <article className="panel p-4">
          <h2 className="display text-2xl font-bold">Fee and wages by client</h2>
          <p className="text-sm text-[var(--muted)]">{data.board.net_profitability_reason}</p>
          <ul className="mt-4 space-y-2 text-sm">
            {data.board.clients_this_week.length === 0 ? <li>No client invoice for this week.</li> : data.board.clients_this_week.map((row) => (
              <li key={row.client_name} className="rounded-xl bg-[var(--canvas)] px-3 py-2">
                <p className="font-semibold">{row.client_name}</p>
                <p>Wages GHS {row.employment_cost} · fee GHS {row.agency_fee} · outstanding GHS {row.outstanding}</p>
              </li>
            ))}
          </ul>
        </article>
      </section>
      <section className="panel mt-6 overflow-x-auto p-4">
        <h2 className="display text-2xl font-bold">Staffing this week</h2>
        <p className="text-sm text-[var(--muted)]">Filled and open posts by factory. An empty cell has no stored shift.</p>
        {data.board.heatmap.length === 0 ? <p className="mt-3 text-sm">No shifts are stored this week.</p> : (
          <div className="mt-4 min-w-[640px] space-y-2 text-xs">
            <div className="grid grid-cols-[180px_repeat(7,1fr)] gap-1 text-[var(--muted)]">
              <span />
              {data.board.attendance_week.map((day) => <span key={day.date} className="text-center">{day.date.slice(5)}</span>)}
            </div>
            {data.board.heatmap.map((site) => (
              <div key={site.site} className="grid grid-cols-[180px_repeat(7,1fr)] gap-1">
                <span className="truncate text-sm">{site.site}</span>
                {site.days.map((cell) => {
                  const tone = cell.filled + cell.unfilled === 0 ? "bg-[var(--canvas)]" : cell.unfilled > 0 ? "bg-[var(--orange)] text-white" : "bg-[var(--blue)] text-white";
                  return <span key={cell.date} className={`rounded-md px-1 py-2 text-center ${tone}`}>{cell.filled + cell.unfilled === 0 ? "—" : `${cell.filled}/${cell.filled + cell.unfilled}`}</span>;
                })}
              </div>
            ))}
          </div>
        )}
      </section>
      <section className="mt-6 grid gap-4 lg:grid-cols-3">
        <article className="panel p-4">
          <h2 className="display text-2xl font-bold">Exceptions</h2>
          <ul className="mt-3 space-y-2 text-sm">
            <li className="rounded-xl bg-[var(--canvas)] px-3 py-2"><Link href="/floor">{data.late} late · {data.absent} absent today</Link></li>
            <li className="rounded-xl bg-[var(--canvas)] px-3 py-2"><Link href="/deployment">{data.unfilled_shifts} unfilled posts</Link></li>
            <li className="rounded-xl bg-[var(--canvas)] px-3 py-2"><Link href="/work">{data.pending_staffing_requests} staffing requests still pending</Link></li>
            <li className="rounded-xl bg-[var(--canvas)] px-3 py-2">{data.expiring_contracts} contracts end within 30 days</li>
          </ul>
        </article>
        <article className="panel p-4">
          <h2 className="display text-2xl font-bold">Recent activity</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {data.board.activity.length === 0 ? <li className="text-[var(--muted)]">No attendance, request, journal, or receipt is stored.</li> : data.board.activity.map((item) => (
              <li key={`${item.at}-${item.text}`} className="rounded-xl bg-[var(--canvas)] px-3 py-2"><Link href={item.href}>{item.text}</Link></li>
            ))}
          </ul>
        </article>
        <article className="panel p-4">
          <h2 className="display text-2xl font-bold">Open alerts</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {data.open_alerts.length === 0 ? <li className="text-[var(--muted)]">No open operational alerts.</li> : data.open_alerts.map((alert) => (
              <li key={alert.message} className="rounded-xl bg-[var(--canvas)] px-3 py-2">{alert.message}</li>
            ))}
          </ul>
        </article>
        <article className="panel p-4">
          <h2 className="display text-2xl font-bold">Certifications and statutory</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {(floor?.certifications ?? []).length === 0 ? <li className="text-[var(--muted)]">No certification expires within 60 days.</li> : floor?.certifications.map((item) => (
              <li key={`${item.employee_id}-${item.name}`} className="rounded-xl bg-[var(--canvas)] px-3 py-2">
                <Link href={`/employees/${item.employee_id}`}>{item.worker_name} · {item.name} · {item.state} {item.expires_on}</Link>
              </li>
            ))}
            <li className="rounded-xl bg-[var(--canvas)] px-3 py-2">{data.board.statutory_note}</li>
            <li className="rounded-xl bg-[var(--canvas)] px-3 py-2">{data.board.payroll_approval_note}</li>
            {data.board.unpaid_invoices.length === 0 ? <li className="rounded-xl bg-[var(--canvas)] px-3 py-2">No unpaid invoice is stored.</li> : data.board.unpaid_invoices.map((row) => (
              <li key={`${row.client_name}-${row.week_start}`} className="rounded-xl bg-[var(--canvas)] px-3 py-2"><Link href="/finance">{row.client_name} · week {row.week_start} · GHS {row.outstanding}</Link></li>
            ))}
          </ul>
        </article>
      </section>
    </Shell>
  );
}
