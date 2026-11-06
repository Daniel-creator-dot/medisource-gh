import { AssignShift } from "@/components/assign-shift";
import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Coverage = {
  shift_id: string;
  client_name: string;
  site_name: string;
  position: string;
  required_skill: string;
  work_date: string;
  starts_at: string;
  ends_at: string;
  recommendations: { employee_id: string; employee_number: string; name: string; reason: string }[];
  blocked: { employee_id: string; employee_number: string; name: string; reason: string }[];
};

type Me = { role: string };

export default async function DeploymentPage() {
  const [result, me] = await Promise.all([apiGet<Coverage[]>("/deployment/coverage/"), apiGet<Me>("/auth/me/")]);
  const canAssign = me.data?.role === "agency_owner" || me.data?.role === "agency_operations" || me.data?.role === "agency_finance";
  return (
    <Shell>
      <p className="text-sm font-semibold tracking-[0.16em] text-[var(--orange)]">AUTOMATION</p>
      <h1 className="display mt-1 text-5xl font-bold">Coverage desk</h1>
      <p className="mt-2 max-w-3xl text-sm text-[var(--muted)]">
        Open posts for this week are matched to workers who hold the skill and have 11 hours since the previous shift. Choosing a recommendation writes the assignment and rebuilds this week&apos;s invoices. A blocked worker is refused.
      </p>
      {result.status === 403 ? <p className="mt-3">{result.message}</p> : null}
      <div className="mt-6 grid gap-4">
        {(result.data ?? []).length === 0 ? <p className="panel p-4 text-sm">No unfilled shifts are stored this week.</p> : null}
        {(result.data ?? []).map((shift) => (
          <article key={shift.shift_id} className="panel overflow-hidden p-0">
            <div className="grid gap-0 lg:grid-cols-[280px_1fr]">
              <div className="bg-[#16130f] p-5 text-white">
                <p className="text-xs tracking-[0.14em] text-white/55">{shift.work_date}</p>
                <h2 className="display mt-2 text-3xl font-bold">{shift.position}</h2>
                <p className="mt-2 text-sm text-white/70">{shift.client_name}<br />{shift.site_name}<br />{shift.starts_at.slice(0, 5)}–{shift.ends_at.slice(0, 5)}</p>
                <p className="mt-4 text-sm text-[var(--orange)]">{shift.required_skill || "No skill stored"}</p>
              </div>
              <div className="p-5">
                <h3 className="text-sm font-semibold">Ready to place</h3>
                <ul className="mt-2">
                  {shift.recommendations.length === 0 ? <li className="text-sm text-[var(--muted)]">Nobody stored meets the skill and rest rule.</li> : null}
                  {shift.recommendations.map((row) => (
                    <li key={row.employee_id} className="border-b border-[var(--line)] py-3 text-sm">
                      <p className="font-semibold">{row.employee_number} {row.name}</p>
                      <p className="text-[var(--muted)]">{row.reason}</p>
                      {canAssign ? <AssignShift shiftId={shift.shift_id} employeeId={row.employee_id} name={row.name} /> : null}
                    </li>
                  ))}
                </ul>
                <h3 className="mt-4 text-sm font-semibold">Held back</h3>
                <ul className="mt-2 text-sm text-[var(--muted)]">
                  {shift.blocked.map((row) => (
                    <li key={row.employee_id} className="py-1">{row.employee_number} {row.name}. {row.reason}</li>
                  ))}
                </ul>
              </div>
            </div>
          </article>
        ))}
      </div>
    </Shell>
  );
}
