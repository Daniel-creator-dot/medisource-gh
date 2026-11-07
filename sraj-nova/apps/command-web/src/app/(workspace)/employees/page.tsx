import Link from "next/link";

import { apiGet } from "@/lib/api";

type Person = {
  id: string;
  agency_employee_number: string;
  first_name: string;
  last_name: string;
  status: string;
  is_demo: boolean;
  deployment: { client_name: string; position: string } | null;
};

export default async function EmployeesPage() {
  const result = await apiGet<Person[]>("/employees/");
  return (
    <>
      <p className="text-sm font-semibold tracking-[0.16em] text-[var(--orange)]">PEOPLE</p>
      <h1 className="display mt-1 text-4xl font-bold">Workforce</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">Open a person for the 360° record. Pay and restricted notes stay with the agency and the worker.</p>
      {result.status === 403 ? <p className="mt-3">{result.message}</p> : null}
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {(result.data ?? []).map((person) => (
          <Link key={person.id} href={`/employees/${person.id}`} className="panel block p-4">
            <p className="text-xs font-semibold tracking-[0.14em] text-[var(--orange)]">{person.agency_employee_number}</p>
            <h2 className="display mt-1 text-3xl font-bold">{person.first_name} {person.last_name}</h2>
            <p className="mt-2 text-sm capitalize text-[var(--muted)]">{person.status}{person.is_demo ? " · sample record" : ""}</p>
            <p className="mt-3 text-sm">{person.deployment ? `${person.deployment.position} · ${person.deployment.client_name}` : "No current factory deployment"}</p>
          </Link>
        ))}
      </div>
    </>
  );
}
