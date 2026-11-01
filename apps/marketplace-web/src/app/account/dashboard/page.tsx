"use client";

import { Card } from "@medisource/ui";
import { useQuery } from "@tanstack/react-query";

import { browserApi } from "@/lib/browser-api";

export default function DashboardPage() {
  const me = useQuery({ queryKey: ["me"], queryFn: () => browserApi.me() });
  const user = me.data?.data;
  if (!user) {
    return <p className="text-sm text-muted">Loading your dashboard…</p>;
  }
  return (
    <div className="grid gap-4">
      <div>
        <h1 className="text-3xl font-semibold text-navy">Dashboard</h1>
        <p className="mt-2 text-sm text-muted">Your account is connected to the API. Orders and appointments are not available yet.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Role</p>
          <p className="mt-2 text-lg font-semibold text-navy">{user.platform_role.replaceAll("_", " ")}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Email</p>
          <p className="mt-2 text-lg font-semibold text-navy">{user.email_verified ? "Verified" : "Not verified"}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Authenticator</p>
          <p className="mt-2 text-lg font-semibold text-navy">{user.mfa_enabled ? "Enabled" : "Not enabled"}</p>
        </Card>
      </div>
      {user.is_demo_account ? (
        <Card className="border-warning/30 bg-amber-50 p-5 text-sm text-ink">
          This is a sample account created by the demo seed. It is not a real customer record.
        </Card>
      ) : null}
    </div>
  );
}
