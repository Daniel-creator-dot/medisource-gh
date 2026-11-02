"use client";

import { useQuery } from "@tanstack/react-query";
import { ShoppingBag } from "lucide-react";
import Link from "next/link";

import { browserApi } from "@/lib/browser-api";

export function CartLink() {
  const cart = useQuery({ queryKey: ["cart"], queryFn: () => browserApi.cart(), retry: false });
  const count = cart.data?.data.item_count ?? 0;
  return (
    <Link
      href="/cart"
      className="relative grid h-10 w-10 place-items-center rounded-full border border-line text-navy hover:bg-canvas"
      aria-label={count === 1 ? "Cart, 1 item" : count > 1 ? `Cart, ${count} items` : "Cart"}
    >
      <ShoppingBag className="h-5 w-5" />
      {count > 0 ? (
        <span className="absolute -right-1 -top-1 grid min-w-5 place-items-center rounded-full bg-teal-dark px-1 text-[11px] font-semibold text-white">
          {count > 99 ? "99+" : count}
        </span>
      ) : null}
    </Link>
  );
}
