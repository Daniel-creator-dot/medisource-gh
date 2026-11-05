import Link from "next/link";

import { Shell } from "@/components/shell";
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
    <Shell>
      <h1 className="text-2xl font-semibold">Workforce</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">Open a person for the 360° record. Pay and restricted notes stay with the agency and the worker.</p>
      {result.status === 403 ? <p className="mt-3">{result.message}</p> : null}
      <div className="mt-4 overflow-x-auto rounded-lg border border-[var(--line)] bg-[var(--card)]">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-[var(--line)] text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2 font-medium">Number</th>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">Status</th>
              <th className="px-3 py-2 font-medium">Current deployment</th>
            </tr>
          </thead>
          <tbody>
            {(result.data ?? []).map((person) => (
              <tr key={person.id} className="border-b border-[var(--line)]">
                <td className="px-3 py-2">
                  <Link className="font-medium underline" href={`/employees/${person.id}`}>
                    {person.agency_employee_number}
                  </Link>
                </td>
                <td className="px-3 py-2">{person.first_name} {person.last_name}</td>
                <td className="px-3 py-2">{person.status}</td>
                <td className="px-3 py-2">{person.deployment ? `${person.deployment.position}, ${person.deployment.client_name}` : "None"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Shell>
  );
}
