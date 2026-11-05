import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Employment = {
  agency_employee_number: string;
  first_name: string;
  last_name: string;
  status: string;
  is_demo: boolean;
  legal_employer?: { kind: string; client_name: string | null };
  deployment: { client_name: string; site_name: string; department: string; position: string } | null;
};

export default async function MyRecordPage() {
  const result = await apiGet<Employment>("/me/employment/");
  const record = result.data;
  return (
    <Shell>
      <h1 className="text-2xl font-semibold">My employment record</h1>
      {result.status === 403 || !record ? (
        <p className="mt-3">{result.message || "This account is not linked to an employee record."}</p>
      ) : (
        <dl className="mt-4 max-w-xl space-y-2 rounded-lg border border-[var(--line)] bg-[var(--card)] p-4 text-sm">
          <div>Employee number: {record.agency_employee_number}</div>
          <div>Name: {record.first_name} {record.last_name}</div>
          <div>Status: {record.status}</div>
          <div>Legal employer: {record.legal_employer?.kind === "client" ? record.legal_employer.client_name : "SRAJ NOVA"}</div>
          <div>Deployment: {record.deployment ? `${record.deployment.position}, ${record.deployment.department}, ${record.deployment.site_name}, ${record.deployment.client_name}` : "None"}</div>
          {record.is_demo ? <p className="text-[var(--muted)]">This worker record is synthetic.</p> : null}
        </dl>
      )}
    </Shell>
  );
}
