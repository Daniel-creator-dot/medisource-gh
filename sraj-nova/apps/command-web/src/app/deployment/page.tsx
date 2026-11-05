import { AssignShift } from "@/components/assign-shift";
import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Coverage = {
  shift_id: string;
  client_name: string;
  site_name: string;
  position: string;
  required_skill: string;
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
      <h1 className="text-2xl font-semibold">Deployment engine</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">
        Open shifts are listed from stored assignments. A recommendation requires the position skill and at least 11 hours between shifts. That rest gap is an operational setting. Assigning a blocked worker is refused.
      </p>
      {result.status === 403 ? <p className="mt-3">{result.message}</p> : null}
      <div className="mt-4 space-y-4">
        {(result.data ?? []).length === 0 ? <p>No unfilled shifts are stored for today.</p> : null}
        {(result.data ?? []).map((shift) => (
          <article key={shift.shift_id} className="rounded-lg border border-[var(--line)] bg-[var(--card)] p-4">
            <h2 className="font-semibold">{shift.position}</h2>
            <p className="text-sm text-[var(--muted)]">{shift.client_name}, {shift.site_name}, {shift.starts_at}–{shift.ends_at}. Skill: {shift.required_skill}.</p>
            <h3 className="mt-3 text-sm font-medium">Recommended</h3>
            <ul className="mt-1 text-sm">
              {shift.recommendations.map((row) => (
                <li key={row.employee_id} className="border-b border-[var(--line)] py-2">
                  {row.employee_number} {row.name}. {row.reason}
                  {canAssign ? <AssignShift shiftId={shift.shift_id} employeeId={row.employee_id} name={row.name} /> : null}
                </li>
              ))}
            </ul>
            <h3 className="mt-3 text-sm font-medium">Blocked despite the skill</h3>
            <ul className="mt-1 text-sm">
              {shift.blocked.map((row) => (
                <li key={row.employee_id}>{row.employee_number} {row.name}. {row.reason}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </Shell>
  );
}
