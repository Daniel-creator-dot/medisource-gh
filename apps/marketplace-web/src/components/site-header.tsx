import Link from "next/link";

import { AccountNav } from "@/components/account-nav";
import { Logo } from "@/components/logo";
import { MobileNav } from "@/components/mobile-nav";

const links = [
  ["/shop", "Shop"],
  ["/categories", "Categories"],
  ["/suppliers", "Suppliers"],
  ["/professionals", "Professionals"],
  ["/about", "About"],
] as const;

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-white/95 backdrop-blur">
      <div className="relative mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4">
        <Logo />
        <nav className="hidden items-center gap-6 text-sm font-medium text-navy md:flex" aria-label="Primary">
          {links.map(([href, label]) => (
            <Link key={href} href={href} className="hover:text-teal-dark">
              {label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <AccountNav />
          <MobileNav />
        </div>
      </div>
    </header>
  );
}
