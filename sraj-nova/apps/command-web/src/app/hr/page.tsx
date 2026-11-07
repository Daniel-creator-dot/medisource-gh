import Link from "next/link";

import { HrDesk } from "@/components/placement-form";
import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Person = {
  id: string;
  agency_employee_number: string;
  first_name: string;
  last_name: string;
  deployment: { client_name: string; site_name?: string; department?: string; position: string } | null;
};

export default async function HrPage() {
  const [result, me] = await Promise.all([apiGet<Person[]>("/employees/"), apiGet<{ role: string }>("/auth/me/")]);
  const canAdd = me.data?.role === "agency_owner" || me.data?.role === "agency_operations" || me.data?.role === "agency_finance";
  return (
    <Shell>
      <p className="text-sm font-semibold tracking-[0.14em] text-[var(--muted)]">HR</p>
      <h1 className="display mt-1 text-4xl font-bold">Add staff</h1>
      <p className="mt-2 max-w-3xl text-sm text-[var(--muted)]">Place a worker in a plant department. The record stores the position and the hourly rate. Tax and net pay stay uncalculated.</p>
      {!canAdd ? <p className="mt-3">Only agency HR can add staff.</p> : result.status === 403 ? <p className="mt-3">{result.message}</p> : <div className="mt-5 grid gap-4 lg:grid-cols-[380px_1fr]"><HrDesk /><div className="space-y-3">{(result.data ?? []).map((person) => (
        <Link key={person.id} href={`/employees/${person.id}`} className="panel block p-4">
          <p className="text-xs font-semibold tracking-[0.12em] text-[var(--muted)]">{person.agency_employee_number}</p>
          <p className="mt-1 font-semibold">{person.first_name} {person.last_name}</p>
          <p className="text-sm text-[var(--muted)]">{person.deployment ? `${person.deployment.position} · ${person.deployment.client_name}` : "No department yet"}</p>
        </Link>
      ))}</div></div>}
    </Shell>
  );
}
