import { RecruitmentDesk } from "@/components/placement-form";
import { apiGet } from "@/lib/api";

type Applicant = {
  id: string;
  first_name: string;
  last_name: string;
  phone: string;
  skill: string;
  status: string;
  note: string;
  is_demo: boolean;
  site_name: string;
  department: string;
  position: string;
  employee_number: string | null;
};

export default async function RecruitmentPage() {
  const result = await apiGet<Applicant[]>("/hr/applicants/");
  return (
    <>
      <p className="text-sm font-semibold tracking-[0.14em] text-[var(--muted)]">RECRUITMENT</p>
      <h1 className="display mt-1 text-4xl font-bold">Recruitment portal</h1>
      <p className="mt-2 max-w-3xl text-sm text-[var(--muted)]">Take an application for a department, move it through screening and offer, then hire the person onto the staff list. Hiring asks for the hourly rate. It does not calculate tax.</p>
      {result.status === 403 ? <p className="mt-3">{result.message}</p> : <div className="mt-5"><RecruitmentDesk applicants={result.data ?? []} /></div>}
    </>
  );
}
