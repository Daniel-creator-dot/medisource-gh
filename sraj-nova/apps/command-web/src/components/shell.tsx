import Link from "next/link";

import { ThemeToggle } from "@/components/theme-toggle";

const links = [
  { href: "/command", label: "Command" },
  { href: "/employees", label: "People" },
  { href: "/deployment", label: "Deployment" },
  { href: "/finance", label: "Finance" },
  { href: "/clients", label: "Clients" },
  { href: "/agency", label: "Agency" },
  { href: "/access", label: "Access" },
  { href: "/me", label: "My record" },
];

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="bg-[var(--navy)] text-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4">
          <Link href="/command" className="text-lg font-semibold tracking-wide">
            SRAJ NOVA
          </Link>
          <nav className="flex flex-wrap gap-4 text-sm">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className="text-white/80 hover:text-white">
                {link.label}
              </Link>
            ))}
          </nav>
          <ThemeToggle />
        </div>
      </header>
      <div className="border-b border-[var(--line)] bg-[var(--card)] px-4 py-2 text-sm text-[var(--muted)]">
        Demonstration data only. The factories below are sample client organizations, not SRAJ NOVA.
      </div>
      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
    </div>
  );
}
