import { Badge, Card } from "@medisource/ui";
import type { SupplierCard as Supplier } from "@medisource/shared-types";
import Link from "next/link";

export function SupplierCard({ supplier }: { supplier: Supplier }) {
  return (
    <Card className="flex h-full flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-medium text-muted">
          {supplier.city}, {supplier.region}
        </p>
        {supplier.is_demo ? <Badge tone="sample">Sample</Badge> : <Badge tone="open">Verified</Badge>}
      </div>
      <h3 className="mt-3 text-lg font-semibold text-navy">
        <Link href={`/suppliers/${supplier.slug}`} className="hover:text-teal-dark">
          {supplier.display_name}
        </Link>
      </h3>
      <p className="mt-2 line-clamp-3 text-sm leading-6 text-muted">{supplier.summary}</p>
      <p className="mt-auto pt-5 text-sm text-navy">
        {`${supplier.active_listing_count ?? 0} public listing${(supplier.active_listing_count ?? 0) === 1 ? "" : "s"}`}
      </p>
    </Card>
  );
}
