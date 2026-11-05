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

const metrics: { label: string; value: (data: Center) => number }[] = [
  { label: "Active workforce", value: (data) => data.active_workforce },
  { label: "Deployed workers", value: (data) => data.deployed_workers },
  { label: "Scheduled today", value: (data) => data.scheduled_today },
  { label: "On duty", value: (data) => data.on_duty },
  { label: "Late", value: (data) => data.late },
  { label: "Absent", value: (data) => data.absent },
  { label: "Unfilled shifts", value: (data) => data.unfilled_shifts },
  { label: "Pending requests", value: (data) => data.pending_staffing_requests },
  { label: "Contracts expiring in 30 days", value: (data) => data.expiring_contracts },
];

export default async function CommandPage() {
  const result = await apiGet<Center>("/command-center/");
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
  return (
    <Shell>
      <h1 className="text-2xl font-semibold">Command center</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">
        Counts for {data.as_of}, scope {data.scope}. Late means a recorded arrival more than 10 minutes after the scheduled start. That grace period is an operational setting.
      </p>
      <section className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric) => (
          <article key={metric.label} className="rounded-lg border border-[var(--line)] bg-[var(--card)] p-4">
            <p className="text-sm text-[var(--muted)]">{metric.label}</p>
            <p className="mt-2 text-3xl font-semibold">{metric.value(data)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 grid gap-4 lg:grid-cols-2">
        <article className="rounded-lg border border-[var(--line)] bg-[var(--card)] p-4">
          <h2 className="font-semibold">Workers by client</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {data.workers_by_client.map((row) => (
              <li key={row.client_id} className="flex justify-between border-b border-[var(--line)] py-2">
                <span>{row.client_name}</span>
                <span>{row.workers}</span>
              </li>
            ))}
          </ul>
        </article>
        <article className="rounded-lg border border-[var(--line)] bg-[var(--card)] p-4">
          <h2 className="font-semibold">Open operational alerts</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {data.open_alerts.map((alert) => (
              <li key={alert.message}>{alert.message}</li>
            ))}
          </ul>
        </article>
      </section>
      <section className="mt-6 rounded-lg border border-[var(--line)] bg-[var(--card)] p-4">
        <h2 className="font-semibold">Payroll and billing</h2>
        <p className="mt-2 text-sm">{data.finance.reason}</p>
        <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
          <div>Weekly gross wages: GHS {data.finance.weekly_gross_payroll}</div>
          <div>Agency fee: GHS {data.finance.agency_fee_revenue}</div>
          <div>Outstanding invoices: GHS {data.finance.outstanding_invoices}</div>
          <div>Net pay and statutory amounts: not calculated</div>
          {"cash_available" in data.finance ? <div>Recorded cash: GHS {data.finance.cash_available}</div> : null}
        </dl>
      </section>
    </Shell>
  );
}
