"use client";

import { MediSourceApiError } from "@medisource/api-client";
import { Button } from "@medisource/ui";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { browserApi } from "@/lib/browser-api";

const links = [
  ["/account/dashboard", "Dashboard"],
  ["/account/addresses", "Addresses"],
  ["/account/notifications", "Notifications"],
  ["/account/settings", "Settings"],
] as const;

export function AccountFrame({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const me = useQuery({ queryKey: ["me"], queryFn: () => browserApi.me() });
  const queryClient = useQueryClient();

  useEffect(() => {
    if (me.error instanceof MediSourceApiError && me.error.status === 401) {
      router.replace("/login");
    }
  }, [me.error, router]);

  async function logout() {
    await browserApi.logout();
    queryClient.clear();
    router.replace("/");
    router.refresh();
  }

  if (me.isLoading) {
    return <div className="mx-auto max-w-6xl px-4 py-16 text-sm text-muted">Loading your account…</div>;
  }
  if (!me.data) {
    return <div className="mx-auto max-w-6xl px-4 py-16 text-sm text-muted">Checking your session…</div>;
  }

  const user = me.data.data;
  return (
    <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 lg:grid-cols-[220px_1fr]">
      <aside>
        <p className="text-sm font-semibold text-navy">
          {user.first_name} {user.last_name}
        </p>
        <p className="mt-1 text-xs text-muted">{user.email}</p>
        <nav className="mt-6 grid gap-1" aria-label="Account">
          {links.map(([href, label]) => (
            <Link
              key={href}
              href={href}
              className={`rounded-xl px-3 py-2 text-sm font-medium ${
                pathname === href ? "bg-white text-navy shadow-sm" : "text-muted hover:bg-white"
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>
        <Button variant="secondary" size="sm" className="mt-4" onClick={logout}>
          Sign out
        </Button>
      </aside>
      <div>{children}</div>
    </div>
  );
}
