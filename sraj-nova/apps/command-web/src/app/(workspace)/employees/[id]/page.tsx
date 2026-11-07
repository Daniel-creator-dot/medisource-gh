import { apiGet } from "@/lib/api";

type Profile = {
  agency_employee_number: string;
  first_name: string;
  last_name: string;
  status: string;
  is_demo: boolean;
  legal_employer: { kind: string; client_name: string | null; starts_on: string } | null;
  deployments: { client_name: string; site_name: string; department: string; position: string; starts_on: string; is_current: boolean }[];
  qualifications: string[];
  attendance: { occurred_at: string; event_type: string; source: string }[];
  leave: { starts_on: string; ends_on: string; status: string }[];
  payments: { status: string; message: string };
  pay_profile: { hourly_rate: string; currency: string } | null;
  certifications: { name: string; expires_on: string | null }[];
  recruitment: { occurred_on: string; summary: string }[];
  hr_notes: { visibility: string; body: string }[];
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="panel p-4">
      <h2 className="font-semibold">{title}</h2>
      <div className="mt-2 text-sm">{children}</div>
    </section>
  );
}

export default async function EmployeeProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await apiGet<Profile>(`/employees/${id}/`);
  const person = result.data;
  if (!person) {
    return (
      <>
        <h1 className="text-2xl font-semibold">Record not available</h1>
        <p className="mt-2 text-sm">{result.message}</p>
      </>
    );
  }
  return (
    <>
      <h1 className="display text-4xl font-bold">{person.first_name} {person.last_name}</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">
        {person.agency_employee_number} · {person.status}
        {person.is_demo ? " · Synthetic demonstration record" : ""}
      </p>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Section title="Employment contract">
          {person.legal_employer ? (
            <p>Legal employer: {person.legal_employer.kind === "client" ? person.legal_employer.client_name : "SRAJ NOVA"}, from {person.legal_employer.starts_on}.</p>
          ) : (
            <p>The legal employer is not shown for this account.</p>
          )}
        </Section>
        <Section title="Pay">
          {person.pay_profile ? <p>Stored hourly rate: {person.pay_profile.currency} {person.pay_profile.hourly_rate}. This is not a payslip.</p> : <p>Compensation is hidden for this account.</p>}
          <p className="mt-2">{person.payments.message}</p>
        </Section>
        <Section title="Deployments">
          <ul className="space-y-2">
            {person.deployments.map((row) => (
              <li key={`${row.starts_on}-${row.client_name}`}>{row.is_current ? "Current" : "Previous"}: {row.position}, {row.department}, {row.site_name}, {row.client_name}</li>
            ))}
          </ul>
        </Section>
        <Section title="Skills and certificates">
          <p>Skills: {person.qualifications.join(", ") || "None recorded"}</p>
          <ul className="mt-2">{person.certifications.map((row) => <li key={row.name}>{row.name}{row.expires_on ? `, expires ${row.expires_on}` : ""}</li>)}</ul>
        </Section>
        <Section title="Recruitment">
          {person.recruitment.length === 0 ? <p>No recruitment history is visible for this account.</p> : person.recruitment.map((row) => <p key={row.summary}>{row.occurred_on}: {row.summary}</p>)}
        </Section>
        <Section title="Leave">
          {person.leave.length === 0 ? <p>No leave requests.</p> : person.leave.map((row) => <p key={row.starts_on}>{row.starts_on} to {row.ends_on}: {row.status}</p>)}
        </Section>
        <Section title="Attendance events">
          {person.attendance.length === 0 ? <p>No attendance events.</p> : person.attendance.map((row) => <p key={row.occurred_at}>{row.occurred_at}: {row.event_type} from {row.source}</p>)}
        </Section>
        <Section title="HR notes">
          {person.hr_notes.length === 0 ? <p>No notes are visible for this account.</p> : person.hr_notes.map((row) => <p key={row.body}>{row.visibility}: {row.body}</p>)}
        </Section>
      </div>
    </>
  );
}
