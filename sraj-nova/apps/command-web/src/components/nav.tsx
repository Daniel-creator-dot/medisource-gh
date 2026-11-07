"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  Briefcase,
  Building2,
  CalendarClock,
  Factory,
  KeyRound,
  Layers,
  Landmark,
  LayoutDashboard,
  UserPlus,
  ListChecks,
  Settings,
  UserRound,
  Users,
  Wallet,
} from "lucide-react";

const agency = ["agency_owner", "agency_operations", "agency_finance"];
const plant = [...agency, "client_user"];

const groups = [
  {
    label: "Operate",
    links: [
      { href: "/command", label: "Command", icon: LayoutDashboard, roles: plant },
      { href: "/work", label: "Actions", icon: ListChecks, roles: plant },
      { href: "/floor", label: "Floor", icon: Factory, roles: plant },
      { href: "/departments", label: "Departments", icon: Layers, roles: plant },
      { href: "/deployment", label: "Coverage", icon: CalendarClock, roles: plant },
    ],
  },
  {
    label: "Money",
    links: [
      { href: "/finance", label: "Finance", icon: Wallet, roles: plant },
      { href: "/accounting", label: "Books", icon: BookOpen, roles: agency },
    ],
  },
  {
    label: "Records",
    links: [
      { href: "/hr", label: "HR", icon: UserPlus, roles: agency },
      { href: "/recruitment", label: "Recruitment", icon: Briefcase, roles: agency },
      { href: "/employees", label: "People", icon: Users, roles: plant },
      { href: "/clients", label: "Clients", icon: Building2, roles: plant },
      { href: "/agency", label: "Agency", icon: Landmark, roles: agency },
      { href: "/access", label: "Roles", icon: KeyRound, roles: ["agency_owner"] },
      { href: "/me", label: "My record", icon: UserRound, roles: ["employee"] },
      { href: "/settings", label: "Settings", icon: Settings, roles: [...plant, "employee"] },
    ],
  },
];

export function Nav({ role }: { role: string }) {
  const path = usePathname();
  return (
    <nav>
      {groups.map((group) => {
        const links = group.links.filter((link) => link.roles.includes(role));
        if (links.length === 0) return null;
        return (
          <div key={group.label}>
            <p className="nav-label">{group.label}</p>
            {links.map((link) => {
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
        );
      })}
    </nav>
  );
}
