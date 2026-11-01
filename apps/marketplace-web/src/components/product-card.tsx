import { Badge, Card } from "@medisource/ui";
import type { ProductCard as Product } from "@medisource/shared-types";
import Link from "next/link";

import { formatMoney } from "@/lib/format";

export function ProductCard({ product }: { product: Product }) {
  return (
    <Card className="flex h-full flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal-dark">{product.category_name}</p>
        {product.is_demo ? <Badge tone="sample">Sample</Badge> : null}
      </div>
      <h3 className="mt-3 text-lg font-semibold text-navy">
        <Link href={`/shop/${product.slug}`} className="hover:text-teal-dark">
          {product.name}
        </Link>
      </h3>
      <p className="mt-1 text-sm text-muted">
        {product.brand} · {product.pack_size}
      </p>
      <p className="mt-4 text-sm text-muted">
        {`${product.supplier_count} supplier${product.supplier_count === 1 ? "" : "s"}`}
      </p>
      <div className="mt-auto flex items-end justify-between pt-5">
        <p className="text-base font-semibold text-navy">
          {product.lowest_price
            ? `From ${formatMoney(product.lowest_price.amount, product.lowest_price.currency)}`
            : "Price unavailable"}
        </p>
        <Link href={`/shop/${product.slug}`} className="text-sm font-semibold text-teal-dark">
          View
        </Link>
      </div>
    </Card>
  );
}
