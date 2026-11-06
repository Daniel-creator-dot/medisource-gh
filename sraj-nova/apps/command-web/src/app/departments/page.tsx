import Link from "next/link";

import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type RosterRow = {
  employee_id: string | null;
  worker_number: string | null;
  worker_name: string | null;
  position: string;
  attendance: string;
  starts_at: string | null;
  ends_at: string | null;
};

type Department = {
  id: string;
  name: string;
  deployed: number;
  filled: number;
  open: number;
  on_duty: number;
  late: number;
  absent: number;
  roster: RosterRow[];
};

type Plant = {
  client_name: string;
  site_name: string;
  city: string;
  region: string;
  departments: Department[];
};

type Board = { as_of: string; note: string; plants: Plant[] };

function attendanceLabel(value: string) {
  if (value === "not_rostered") return "Not on today's shift";
  if (value === "open") return "Open post";
  return value.replace(/_/g, " ");
}

export default async function DepartmentsPage() {
  const result = await apiGet<Board>("/departments/");
  const board = result.data;
  if (result.status === 403 || !board) {
    return (
      <Shell>
        <h1 className="display text-4xl font-bold">Departments</h1>
        <p className="mt-3">{result.message || "This account cannot open the department rosters."}</p>
      </Shell>
    );
  }
  return (
    <Shell>
      <p className="text-sm font-semibold tracking-[0.14em] text-[var(--muted)]">CEMENT PLANT</p>
      <h1 className="display mt-1 text-4xl font-bold">Departments</h1>
      <p className="mt-2 max-w-3xl text-sm text-[var(--muted)]">{board.as_of}. {board.note}</p>
      <div className="mt-6 space-y-8">
        {board.plants.map((plant) => (
          <section key={`${plant.client_name}-${plant.site_name}`}>
            <h2 className="text-lg font-semibold">{plant.site_name}</h2>
            <p className="text-sm text-[var(--muted)]">{plant.client_name} · {plant.city}, {plant.region}</p>
            <div className="mt-3 grid gap-3 lg:grid-cols-2">
              {plant.departments.map((department) => (
                <article key={department.id} id={department.id} className="panel p-4">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-lg font-semibold">{department.name}</h3>
                    <p className="text-sm text-[var(--muted)]">{department.deployed} deployed · {department.filled} on shift · {department.open} open</p>
                  </div>
                  <p className="mt-1 text-sm text-[var(--muted)]">{department.on_duty} on duty · {department.late} late · {department.absent} absent</p>
                  {department.roster.length === 0 ? <p className="mt-3 text-sm text-[var(--muted)]">No one is deployed here and no post is stored for today.</p> : (
                    <ul className="mt-3 space-y-2">
                      {department.roster.map((row) => (
                        <li key={`${row.position}-${row.worker_number ?? "open"}-${row.starts_at ?? "none"}`} className="rounded-xl bg-[var(--canvas)] px-3 py-2 text-sm">
                          <div className="flex items-start justify-between gap-3">
                            <div>
                              <p className="font-semibold">{row.position}</p>
                              {row.employee_id ? (
                                <Link className="text-[var(--blue)]" href={`/employees/${row.employee_id}`}>{row.worker_number} {row.worker_name}</Link>
                              ) : <p>No worker assigned</p>}
                              {row.starts_at ? <p className="text-[var(--muted)]">{row.starts_at}–{row.ends_at}</p> : null}
                            </div>
                            <span className="pill">{attendanceLabel(row.attendance)}</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                  {department.open > 0 ? <Link className="mt-3 inline-flex text-sm font-semibold text-[var(--blue)]" href="/deployment">Fill the open post</Link> : null}
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>
    </Shell>
  );
}
