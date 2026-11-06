"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/command", label: "Command" },
  { href: "/floor", label: "Floor" },
  { href: "/employees", label: "People" },
  { href: "/deployment", label: "Deployment" },
  { href: "/finance", label: "Finance" },
  { href: "/accounting", label: "Books" },
  { href: "/clients", label: "Clients" },
  { href: "/agency", label: "Agency" },
  { href: "/access", label: "Access" },
  { href: "/me", label: "My record" },
];

export function Nav() {
  const path = usePathname();
  return (
    <nav className="flex flex-wrap gap-1 text-sm">
      {links.map((link) => {
        const active = path === link.href || path.startsWith(`${link.href}/`);
        return (
          <Link
            key={link.href}
            href={link.href}
            className={active ? "rounded-full bg-white px-3 py-1 font-medium text-[#0b1f33]" : "rounded-full px-3 py-1 text-white/75 hover:bg-white/10 hover:text-white"}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
