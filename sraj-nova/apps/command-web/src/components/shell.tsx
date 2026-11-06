import Link from "next/link";

import { Mark } from "@/components/mark";
import { Nav } from "@/components/nav";
import { ThemeToggle } from "@/components/theme-toggle";
import { WorkspaceSearch } from "@/components/workspace-search";
import { apiGet } from "@/lib/api";

const roleLabels: Record<string, string> = {
  agency_owner: "Agency owner",
  agency_operations: "Agency operations",
  agency_finance: "Agency finance",
  client_user: "Client user",
  employee: "Employee",
};

export async function Shell({ children }: { children: React.ReactNode }) {
  const me = await apiGet<{ first_name: string; last_name: string; role: string }>("/auth/me/");
  const role = me.data?.role ?? "";
  const name = me.data ? `${me.data.first_name} ${me.data.last_name}`.trim() : "";
  return (
    <div className="app-shell">
      <aside className="rail">
        <Link href={role === "employee" ? "/me" : "/command"} aria-label="SRAJ NOVA command center" className="px-2">
          <Mark />
        </Link>
        <Nav role={role} />
        <div className="mt-auto">
          <ThemeToggle />
        </div>
      </aside>
      <div className="stage">
        <div className="topbar">
          <WorkspaceSearch />
          <p className="hidden text-sm text-[var(--muted)] lg:block">{name} · {roleLabels[role] ?? "Signed in"}</p>
        </div>
        <main>{children}</main>
      </div>
    </div>
  );
}
