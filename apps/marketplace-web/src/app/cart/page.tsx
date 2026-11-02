import type { Metadata } from "next";

import { CartView } from "@/components/cart-view";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Cart" };

export default function CartPage() {
  return (
    <>
      <PageHeader
        eyebrow="Cart"
        title="Your cart"
        body="Quantities are checked against the supplier listing. Checkout does not take payment in this release."
      />
      <div className="mx-auto max-w-6xl px-4 py-10">
        <CartView />
      </div>
    </>
  );
}
