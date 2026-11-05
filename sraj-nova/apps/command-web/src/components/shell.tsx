import Link from "next/link";

import { Mark } from "@/components/mark";
import { Nav } from "@/components/nav";
import { ThemeToggle } from "@/components/theme-toggle";

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b-2 border-[var(--orange)] bg-[#0b1f33] text-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <Link href="/command" aria-label="SRAJ NOVA command center">
            <Mark light />
          </Link>
          <Nav />
          <ThemeToggle />
        </div>
      </header>
      <div className="border-b border-[var(--line)] bg-[var(--card)] px-4 py-2 text-sm text-[var(--muted)]">
        Demonstration data only. The factories shown are sample client organizations. SRAJ NOVA is the agency.
      </div>
      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
    </div>
  );
}
