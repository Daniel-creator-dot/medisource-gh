"use client";

import { MediSourceApiError } from "@medisource/api-client";
import { Badge, Button, Card } from "@medisource/ui";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

import { EmptyState, ErrorState } from "@/components/states";
import { browserApi } from "@/lib/browser-api";
import { formatMoney } from "@/lib/format";

export function CartView() {
  const queryClient = useQueryClient();
  const cart = useQuery({ queryKey: ["cart"], queryFn: () => browserApi.cart() });
  const [checkoutMessage, setCheckoutMessage] = useState<string | null>(null);
  const [checkoutLines, setCheckoutLines] = useState<string[]>([]);

  const update = useMutation({
    mutationFn: ({ id, quantity }: { id: string; quantity: number }) => browserApi.updateCartLine(id, quantity),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
  });
  const remove = useMutation({
    mutationFn: (id: string) => browserApi.removeCartLine(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
  });
  const checkout = useMutation({
    mutationFn: () => browserApi.checkoutCart(),
    onSuccess: () => {
      setCheckoutMessage("Checkout did not open. No payment was taken.");
      setCheckoutLines([]);
    },
    onError: (error) => {
      if (error instanceof MediSourceApiError) {
        setCheckoutMessage(error.message);
        const details = error.details as { lines?: { product_name: string; reason: string }[] } | null;
        setCheckoutLines(details?.lines?.map((line) => `${line.product_name}: ${line.reason}`) ?? []);
        return;
      }
      setCheckoutMessage("Checkout could not be completed.");
      setCheckoutLines([]);
    },
  });

  if (cart.isPending) {
    return <div className="h-48 animate-pulse rounded-3xl bg-white" />;
  }
  if (cart.isError) {
    const message = cart.error instanceof MediSourceApiError ? cart.error.message : "The cart could not be loaded.";
    return <ErrorState title="Cart unavailable" body={message} />;
  }

  const data = cart.data.data;
  if (data.lines.length === 0) {
    return (
      <div>
        <EmptyState
          title="Your cart is empty"
          body="Browse the shop and save a listing here. Sample records and authorized pharmaceuticals can be reviewed, and checkout stays closed."
        />
        <Link href="/shop" className="mt-4 inline-block text-sm font-semibold text-teal-dark">
          Browse the shop
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.4fr_0.6fr]">
      <ul className="grid gap-4">
        {data.lines.map((line) => (
          <li key={line.id}>
            <Card className="p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Link href={`/shop/${line.product_slug}`} className="text-lg font-semibold text-navy hover:text-teal-dark">
                      {line.product_name}
                    </Link>
                    {line.is_demo ? <Badge tone="sample">Sample</Badge> : null}
                  </div>
                  <Link href={`/suppliers/${line.supplier_slug}`} className="mt-1 block text-sm text-muted hover:text-teal-dark">
                    {line.supplier_name}
                  </Link>
                </div>
                <p className="font-semibold text-navy">{formatMoney(line.line_total, line.currency)}</p>
              </div>
              <p className="mt-3 text-sm text-muted">
                {formatMoney(line.price_amount, line.currency)} each · MOQ {line.minimum_order_quantity} · Stock {line.stock_quantity}
              </p>
              {line.purchase_block_reason ? <p className="mt-2 text-sm text-warning">{line.purchase_block_reason}</p> : null}
              <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
                <label className="text-sm">
                  <span className="sr-only">Quantity for {line.product_name}</span>
                  <input
                    type="number"
                    min={line.minimum_order_quantity}
                    max={line.stock_quantity}
                    defaultValue={line.quantity}
                    key={`${line.id}-${line.quantity}`}
                    onBlur={(event) => {
                      const quantity = Number(event.target.value);
                      if (quantity !== line.quantity && quantity >= line.minimum_order_quantity && quantity <= line.stock_quantity) {
                        update.mutate({ id: line.id, quantity });
                      }
                    }}
                    className="h-11 w-28 rounded-full border border-line px-4 text-sm"
                  />
                </label>
                <Button
                  variant="danger"
                  size="sm"
                  disabled={remove.isPending}
                  onClick={() => remove.mutate(line.id)}
                >
                  Remove
                </Button>
              </div>
              {update.isError ? <p className="mt-2 text-sm text-danger">The quantity could not be updated.</p> : null}
            </Card>
          </li>
        ))}
      </ul>
      <Card className="h-fit p-5">
        <h2 className="text-lg font-semibold text-navy">Summary</h2>
        <dl className="mt-4 flex items-center justify-between text-sm">
          <dt className="text-muted">Subtotal</dt>
          <dd className="font-semibold text-navy">{formatMoney(data.subtotal.amount, data.subtotal.currency)}</dd>
        </dl>
        <p className="mt-4 text-sm leading-6 text-muted">{data.checkout_message}</p>
        <Button className="mt-5 w-full" disabled={checkout.isPending} onClick={() => checkout.mutate()}>
          {checkout.isPending ? "Checking…" : "Review checkout"}
        </Button>
        {checkoutMessage ? <p className="mt-3 text-sm leading-6 text-navy">{checkoutMessage}</p> : null}
        {checkoutLines.length > 0 ? (
          <ul className="mt-3 space-y-2 text-sm text-warning">
            {checkoutLines.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        ) : null}
        <Link href="/shop" className="mt-4 inline-block text-sm font-semibold text-teal-dark">
          Continue browsing
        </Link>
      </Card>
    </div>
  );
}
