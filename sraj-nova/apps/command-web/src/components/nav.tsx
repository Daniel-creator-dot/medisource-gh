"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/command", label: "Command" },
  { href: "/work", label: "Actions" },
  { href: "/floor", label: "Floor" },
  { href: "/deployment", label: "Coverage" },
  { href: "/employees", label: "People" },
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
    <nav>
      {links.map((link) => {
        const active = path === link.href || path.startsWith(`${link.href}/`);
        return (
          <Link key={link.href} href={link.href} data-active={active ? "true" : "false"}>
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
