import { MediSourceApiError } from "@medisource/api-client";
import { Badge, Card } from "@medisource/ui";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { getSupplier } from "@/lib/catalog";
import { formatMoney } from "@/lib/format";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  return { title: slug.replaceAll("-", " ") };
}

export default async function SupplierPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  let supplier: Awaited<ReturnType<typeof getSupplier>>["data"];
  try {
    supplier = (await getSupplier(slug)).data;
  } catch (error) {
    if (error instanceof MediSourceApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }
  return (
      <article className="mx-auto max-w-6xl px-4 py-12">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-4xl font-semibold tracking-tight text-navy">{supplier.display_name}</h1>
          {supplier.is_demo ? <Badge tone="sample">Sample</Badge> : <Badge tone="open">Verified</Badge>}
        </div>
        <p className="mt-3 text-muted">
          {supplier.city}, {supplier.region}
        </p>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-ink">{supplier.summary}</p>
        {supplier.demo_label ? <p className="mt-4 text-sm text-warning">{supplier.demo_label}</p> : null}
        <h2 className="mt-10 text-2xl font-semibold text-navy">Listings</h2>
        <div className="mt-4 grid gap-4">
          {supplier.listings.map((listing) => (
            <Card key={listing.id} className="p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <Link href={`/shop/${listing.product_slug}`} className="text-lg font-semibold text-navy hover:text-teal-dark">
                    {listing.product_name}
                  </Link>
                  <p className="mt-1 text-sm text-muted">SKU {listing.sku}</p>
                </div>
                <p className="text-lg font-semibold text-navy">{formatMoney(listing.price_amount, listing.currency)}</p>
              </div>
              <p className="mt-3 text-sm text-muted">
                Stock {listing.stock_quantity} · MOQ {listing.minimum_order_quantity} · {listing.warehouse_name}
              </p>
              {listing.purchase_block_reason ? <p className="mt-2 text-sm text-warning">{listing.purchase_block_reason}</p> : null}
            </Card>
          ))}
        </div>
      </article>
  );
}
