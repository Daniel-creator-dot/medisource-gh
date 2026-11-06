import Link from "next/link";

import { Mark } from "@/components/mark";
import { Nav } from "@/components/nav";
import { ThemeToggle } from "@/components/theme-toggle";
import { WorkspaceSearch } from "@/components/workspace-search";

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="rail">
        <Link href="/command" aria-label="SRAJ NOVA command center" className="px-2">
          <Mark />
        </Link>
        <Nav />
        <div className="mt-auto">
          <ThemeToggle />
        </div>
      </aside>
      <div className="stage">
        <div className="topbar">
          <WorkspaceSearch />
          <p className="hidden text-sm text-[var(--muted)] lg:block">Live workspace. Amounts come from stored records.</p>
        </div>
        <main>{children}</main>
      </div>
    </div>
  );
}
