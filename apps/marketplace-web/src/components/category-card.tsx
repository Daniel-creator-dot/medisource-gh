import { Badge, Card } from "@medisource/ui";
import type { Category } from "@medisource/shared-types";
import Link from "next/link";

export function CategoryCard({ category }: { category: Category }) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-navy">
          <Link href={`/shop?category=${category.slug}`} className="hover:text-teal-dark">
            {category.name}
          </Link>
        </h3>
        <Badge tone={category.checkout_enabled ? "open" : "closed"}>
          {category.checkout_enabled ? "Policy open" : "Checkout closed"}
        </Badge>
      </div>
      <p className="mt-2 text-sm leading-6 text-muted">{category.description}</p>
      <p className="mt-4 text-sm font-medium text-navy">{category.product_count} public products</p>
    </Card>
  );
}
