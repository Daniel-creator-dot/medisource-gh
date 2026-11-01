import { MediSourceApiError } from "@medisource/api-client";
import type { Metadata } from "next";

import { PageHeader } from "@/components/page-header";
import { EmptyState, ErrorState } from "@/components/states";
import { SupplierCard } from "@/components/supplier-card";
import { getSuppliers } from "@/lib/catalog";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Suppliers" };

export default async function SuppliersPage() {
  let suppliers: Awaited<ReturnType<typeof getSuppliers>>["data"] | null = null;
  let errorMessage: string | null = null;
  try {
    suppliers = (await getSuppliers()).data;
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
        {suppliers.length === 0 ? (
          <EmptyState title="No public suppliers" body="Verified or sample suppliers will appear here after they are in the database." />
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {suppliers.map((supplier) => (
              <SupplierCard key={supplier.id} supplier={supplier} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
