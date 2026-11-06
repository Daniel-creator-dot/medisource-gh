import Link from "next/link";

import { Mark } from "@/components/mark";
import { Nav } from "@/components/nav";
import { ThemeToggle } from "@/components/theme-toggle";

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="rail">
        <Link href="/command" aria-label="SRAJ NOVA command center">
          <Mark light />
        </Link>
        <p className="px-2 text-xs leading-5 text-white/55">Factory workforce, coverage, and client billing.</p>
        <Nav />
        <div className="mt-auto">
          <ThemeToggle />
        </div>
      </aside>
      <div className="stage">
        <div className="banner">Sample factories only. SRAJ NOVA is the agency. Amounts come from stored shifts, rates, and journals.</div>
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">{children}</main>
      </div>
    </div>
  );
}
