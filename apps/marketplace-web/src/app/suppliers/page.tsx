import { MediSourceApiError } from "@medisource/api-client";
import type { Metadata } from "next";
import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import { EmptyState, ErrorState } from "@/components/states";
import { SupplierCard } from "@/components/supplier-card";
import { getSuppliers } from "@/lib/catalog";
import { firstParam } from "@/lib/format";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Suppliers" };

export default async function SuppliersPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const q = firstParam(params.q) ?? "";
  const region = firstParam(params.region) ?? "";
  let suppliers: Awaited<ReturnType<typeof getSuppliers>>["data"] | null = null;
  let regions: string[] = [];
  let errorMessage: string | null = null;
  try {
    const [filtered, all] = await Promise.all([getSuppliers({ q, region }), getSuppliers({})]);
    suppliers = filtered.data;
    regions = [...new Set(all.data.map((supplier) => supplier.region))].sort();
  } catch (error) {
    errorMessage = error instanceof MediSourceApiError ? error.message : "Suppliers could not be loaded.";
  }
  if (errorMessage || !suppliers) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <ErrorState title="Directory unavailable" body={errorMessage ?? "Suppliers could not be loaded."} />
      </div>
    );
  }
  return (
    <>
      <PageHeader
        eyebrow="Suppliers"
        title="Supplier directory"
        body="Public profiles are limited to demo and verified suppliers. Internal notes, bank details, and other members' records are not on this page."
      />
      <div className="mx-auto max-w-6xl px-4 py-10">
        <form action="/suppliers" className="grid gap-3 rounded-2xl border border-line bg-white p-4 md:grid-cols-[1fr_220px_auto]">
          <input
            name="q"
            defaultValue={q}
            placeholder="Search suppliers or cities"
            aria-label="Search suppliers"
            className="h-12 rounded-full border border-line px-5 text-sm outline-none focus-visible:ring-2 focus-visible:ring-teal"
          />
          <select name="region" defaultValue={region} aria-label="Region" className="h-12 rounded-full border border-line bg-white px-4 text-sm">
            <option value="">All regions</option>
            {regions.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
          <button type="submit" className="h-12 rounded-full bg-navy px-5 text-sm font-semibold text-white">
            Apply
          </button>
        </form>
        {q || region ? (
          <Link href="/suppliers" className="mt-4 inline-block text-sm font-semibold text-teal-dark">
            Clear filters
          </Link>
        ) : null}
        {suppliers.length === 0 ? (
          <div className="mt-8">
            <EmptyState title="No public suppliers" body="Try another search, or wait until a verified or sample supplier is in the database." />
          </div>
        ) : (
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            {suppliers.map((supplier) => (
              <SupplierCard key={supplier.id} supplier={supplier} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
