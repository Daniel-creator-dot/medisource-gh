"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  Building2,
  CalendarClock,
  Factory,
  KeyRound,
  Layers,
  Landmark,
  LayoutDashboard,
  ListChecks,
  UserRound,
  Users,
  Wallet,
} from "lucide-react";

const groups = [
  {
    label: "Operate",
    links: [
      { href: "/command", label: "Command", icon: LayoutDashboard },
      { href: "/work", label: "Actions", icon: ListChecks },
      { href: "/floor", label: "Floor", icon: Factory },
      { href: "/departments", label: "Departments", icon: Layers },
      { href: "/deployment", label: "Coverage", icon: CalendarClock },
    ],
  },
  {
    label: "Money",
    links: [
      { href: "/finance", label: "Finance", icon: Wallet },
      { href: "/accounting", label: "Books", icon: BookOpen },
    ],
  },
  {
    label: "Records",
    links: [
      { href: "/employees", label: "People", icon: Users },
      { href: "/clients", label: "Clients", icon: Building2 },
      { href: "/agency", label: "Agency", icon: Landmark },
      { href: "/access", label: "Access", icon: KeyRound },
      { href: "/me", label: "My record", icon: UserRound },
    ],
  },
];

export function Nav() {
  const path = usePathname();
  return (
    <nav>
      {groups.map((group) => (
        <div key={group.label}>
          <p className="nav-label">{group.label}</p>
          {group.links.map((link) => {
            const active = path === link.href || path.startsWith(`${link.href}/`);
            const Icon = link.icon;
            return (
              <Link key={link.href} href={link.href} data-active={active ? "true" : "false"}>
                <Icon aria-hidden="true" size={18} />
                {link.label}
              </Link>
            );
          })}
        </div>
      ))}
    </nav>
  );
}
