"use client";

import { MediSourceApiError } from "@medisource/api-client";
import { Card } from "@medisource/ui";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { ErrorState } from "@/components/states";
import { browserApi } from "@/lib/browser-api";
import { formatMoney } from "@/lib/format";

export default function DashboardPage() {
  const me = useQuery({ queryKey: ["me"], queryFn: () => browserApi.me(), retry: false });
  const cart = useQuery({ queryKey: ["cart"], queryFn: () => browserApi.cart(), retry: false });

  if (me.isPending) {
    return <p className="text-sm text-muted">Loading your dashboard…</p>;
  }
  if (me.isError || !me.data) {
    const message = me.error instanceof MediSourceApiError ? me.error.message : "Your account could not be loaded.";
    return <ErrorState title="Dashboard unavailable" body={message} />;
  }

  const user = me.data.data;
  const itemCount = cart.data?.data.item_count ?? 0;
  const subtotal = cart.data?.data.subtotal;
  return (
    <div className="grid gap-4">
      <div>
        <h1 className="text-3xl font-semibold text-navy">
          {user.first_name} {user.last_name}
        </h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          Your account is connected to the API. Orders and appointments are not part of this release.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Role</p>
          <p className="mt-2 text-lg font-semibold capitalize text-navy">{user.platform_role.replaceAll("_", " ")}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Email</p>
          <p className="mt-2 text-lg font-semibold text-navy">{user.email_verified ? "Verified" : "Not verified"}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Authenticator</p>
          <p className="mt-2 text-lg font-semibold text-navy">{user.mfa_enabled ? "Enabled" : "Not enabled"}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Cart</p>
          <p className="mt-2 text-lg font-semibold text-navy">
            {cart.isPending ? "Loading…" : `${itemCount} item${itemCount === 1 ? "" : "s"}`}
          </p>
          {subtotal ? <p className="mt-1 text-sm text-muted">{formatMoney(subtotal.amount, subtotal.currency)}</p> : null}
          <Link href="/cart" className="mt-3 inline-block text-sm font-semibold text-teal-dark">
            Open cart
          </Link>
        </Card>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-5">
          <h2 className="font-semibold text-navy">Shop</h2>
          <p className="mt-2 text-sm leading-6 text-muted">Search products, filter by category or supplier, and open a listing.</p>
          <Link href="/shop" className="mt-3 inline-block text-sm font-semibold text-teal-dark">
            Browse products
          </Link>
        </Card>
        <Card className="p-5">
          <h2 className="font-semibold text-navy">Suppliers</h2>
          <p className="mt-2 text-sm leading-6 text-muted">Sample storefronts are labelled. Pending suppliers stay out of the directory.</p>
          <Link href="/suppliers" className="mt-3 inline-block text-sm font-semibold text-teal-dark">
            View suppliers
          </Link>
        </Card>
        <Card className="p-5">
          <h2 className="font-semibold text-navy">Professionals</h2>
          <p className="mt-2 text-sm leading-6 text-muted">The directory is live. No sample clinicians are published.</p>
          <Link href="/professionals" className="mt-3 inline-block text-sm font-semibold text-teal-dark">
            Open directory
          </Link>
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
