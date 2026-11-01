import { MediSourceApiError } from "@medisource/api-client";
import { Badge, Card } from "@medisource/ui";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { getProduct } from "@/lib/catalog";
import { formatMoney } from "@/lib/format";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  return { title: slug.replaceAll("-", " ") };
}

export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  let product: Awaited<ReturnType<typeof getProduct>>["data"];
  try {
    product = (await getProduct(slug)).data;
  } catch (error) {
    if (error instanceof MediSourceApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }
  return (
      <article className="mx-auto max-w-6xl px-4 py-12">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal-dark">{product.category_name}</p>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <h1 className="text-4xl font-semibold tracking-tight text-navy">{product.name}</h1>
          {product.is_demo ? <Badge tone="sample">Sample</Badge> : null}
        </div>
        <p className="mt-3 text-muted">
          {product.brand} · {product.manufacturer} · {product.pack_size}
        </p>
        {product.demo_label ? <p className="mt-4 max-w-3xl text-sm leading-6 text-warning">{product.demo_label}</p> : null}
        <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-navy">Master record</h2>
            <p className="mt-3 text-sm leading-7 text-ink">{product.description}</p>
            <dl className="mt-6 grid gap-3 text-sm">
              <Row label="Specification" value={product.specification} />
              <Row label="Unit" value={product.unit_of_measure} />
              <Row label="Generic name" value={product.generic_name || "Not applicable"} />
              <Row label="Strength" value={product.strength || "Not applicable"} />
              <Row label="Dosage form" value={product.dosage_form || "Not applicable"} />
              <Row label="GTIN" value={product.gtin || "Not recorded"} />
              <Row label="Regulatory notes" value={product.regulatory_notes || "None recorded"} />
            </dl>
          </Card>
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-navy">Supplier listings</h2>
            <p className="mt-2 text-sm text-muted">
              {product.can_purchase
                ? "At least one listing can be purchased."
                : product.purchase_block_reason}
            </p>
            <ul className="mt-5 space-y-4">
              {product.listings.map((listing) => (
                <li key={listing.id} className="rounded-2xl border border-line p-4">
                  <div className="flex items-start justify-between gap-3">
                    <Link href={`/suppliers/${listing.supplier.slug}`} className="font-semibold text-navy hover:text-teal-dark">
                      {listing.supplier.display_name}
                    </Link>
                    <p className="font-semibold text-navy">{formatMoney(listing.price_amount, listing.currency)}</p>
                  </div>
                  <p className="mt-2 text-sm text-muted">
                    Stock {listing.stock_quantity} · MOQ {listing.minimum_order_quantity} · Lead time {listing.lead_time_days} days
                  </p>
                  <p className="mt-1 text-sm text-muted">
                    {listing.warehouse_name} · {listing.delivery_zones.join(", ")}
                  </p>
                  {listing.purchase_block_reason ? (
                    <p className="mt-3 text-sm text-warning">{listing.purchase_block_reason}</p>
                  ) : null}
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </article>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid gap-1 border-t border-line pt-3 sm:grid-cols-[160px_1fr]">
      <dt className="font-medium text-navy">{label}</dt>
      <dd className="text-muted">{value}</dd>
    </div>
  );
}
