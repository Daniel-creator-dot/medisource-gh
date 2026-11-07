import { WorkDesk, type WorkOptions } from "@/components/work-desk";
import { apiGet } from "@/lib/api";

export default async function WorkPage() {
  const result = await apiGet<WorkOptions>("/work/options/");
  return (
    <>
      <p className="text-sm font-semibold tracking-[0.16em] text-[var(--orange)]">DO THE WORK</p>
      <h1 className="display mt-1 text-5xl font-bold">Actions</h1>
      <p className="mt-2 max-w-3xl text-sm text-[var(--muted)]">
        These buttons write records. A post can be left open for Coverage to fill. A punch is added to the attendance log. A staffing request stays pending until someone acts on it.
      </p>
      {result.status === 403 || !result.data ? <p className="mt-4">{result.message || "This account cannot open actions."}</p> : <div className="mt-6"><WorkDesk options={result.data} /></div>}
    </>
  );
}
