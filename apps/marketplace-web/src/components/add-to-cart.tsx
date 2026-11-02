"use client";

import { MediSourceApiError } from "@medisource/api-client";
import { Button } from "@medisource/ui";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { browserApi } from "@/lib/browser-api";

export function AddToCart({
  listingId,
  minimum,
  stock,
  blocked,
}: {
  listingId: string;
  minimum: number;
  stock: number;
  blocked: string | null;
}) {
  const queryClient = useQueryClient();
  const [quantity, setQuantity] = useState(minimum);
  const [message, setMessage] = useState<string | null>(null);
  const [tone, setTone] = useState<"ok" | "error">("ok");
  const unavailable = stock < minimum;
  const mutation = useMutation({
    mutationFn: () => browserApi.addCartLine(listingId, quantity),
    onSuccess: async () => {
      setTone("ok");
      setMessage("Saved in your cart. Checkout stays closed for sample records and pharmaceuticals.");
      await queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
    onError: (error) => {
      setTone("error");
      setMessage(error instanceof MediSourceApiError ? error.message : "The item could not be added.");
    },
  });

  return (
    <form
      className="mt-4 grid gap-3"
      onSubmit={(event) => {
        event.preventDefault();
        setMessage(null);
        if (quantity < minimum || quantity > stock) {
          setTone("error");
          setMessage(`Enter a quantity from ${minimum} to ${stock}.`);
          return;
        }
        mutation.mutate();
      }}
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <label className="text-sm sm:w-28">
          <span className="mb-1 block font-medium text-navy">Quantity</span>
          <input
            type="number"
            min={minimum}
            max={stock}
            value={quantity}
            aria-label="Quantity"
            onChange={(event) => setQuantity(Number(event.target.value))}
            className="h-11 w-full rounded-full border border-line px-4 text-sm outline-none focus-visible:ring-2 focus-visible:ring-teal"
          />
        </label>
        <Button type="submit" disabled={unavailable || mutation.isPending} className="w-full sm:w-auto">
          {mutation.isPending ? "Adding…" : "Add to cart"}
        </Button>
      </div>
      {unavailable ? <p className="text-sm text-warning">Available stock is below the minimum order.</p> : null}
      {blocked ? (
        <p className="text-sm leading-6 text-warning">
          {blocked} The line can still be saved so you can review it. It cannot be checked out.
        </p>
      ) : null}
      {message ? <p className={`text-sm ${tone === "error" ? "text-danger" : "text-navy"}`}>{message}</p> : null}
    </form>
  );
}
