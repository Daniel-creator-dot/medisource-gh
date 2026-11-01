"use client";

import { MediSourceApiError, apiRequest } from "@medisource/api-client";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button, Card, ConfirmDialog, Input, Label } from "@medisource/ui";
import type { Address, Envelope } from "@medisource/shared-types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import type { ReactNode } from "react";
import { z } from "zod";

import { EmptyState } from "@/components/states";

const schema = z.object({
  label: z.string().min(1),
  recipient_name: z.string().min(1),
  phone_number: z.string().optional(),
  line1: z.string().min(1),
  line2: z.string().optional(),
  city: z.string().min(1),
  region: z.string().min(1),
  postal_code: z.string().optional(),
  country: z.string().length(2),
  is_default: z.boolean(),
});

async function csrf() {
  const result = await apiRequest<Envelope<{ csrf_token: string }>>("/api/v1/auth/csrf/");
  return result.data.csrf_token;
}

export default function AddressesPage() {
  const queryClient = useQueryClient();
  const addresses = useQuery({
    queryKey: ["addresses"],
    queryFn: () => apiRequest<Envelope<Address[]>>("/api/v1/account/addresses/"),
  });
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: {
      label: "Home",
      recipient_name: "",
      phone_number: "",
      line1: "",
      line2: "",
      city: "Accra",
      region: "Greater Accra",
      postal_code: "",
      country: "GH",
      is_default: false,
    },
  });
  const create = useMutation({
    mutationFn: async (values: z.infer<typeof schema>) =>
      apiRequest<Envelope<Address>>("/api/v1/account/addresses/", {
        method: "POST",
        body: values,
        csrfToken: await csrf(),
      }),
    onSuccess: async () => {
      form.reset();
      await queryClient.invalidateQueries({ queryKey: ["addresses"] });
    },
  });
  const remove = useMutation({
    mutationFn: async (id: string) =>
      apiRequest<Envelope<{ deleted: boolean }>>(`/api/v1/account/addresses/${id}/`, {
        method: "DELETE",
        csrfToken: await csrf(),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["addresses"] });
    },
  });

  const rows = addresses.data?.data ?? [];
  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-semibold text-navy">Addresses</h1>
        <p className="mt-2 text-sm text-muted">Only your addresses are returned by the API.</p>
      </div>
      {rows.length === 0 ? (
        <EmptyState title="No addresses yet" body="Add a delivery address for the orders that will come in the next release." />
      ) : (
        <div className="grid gap-3">
          {rows.map((address) => (
            <Card key={address.id} className="flex items-start justify-between gap-4 p-4">
              <div>
                <p className="font-semibold text-navy">
                  {address.label}
                  {address.is_default ? " · Default" : ""}
                </p>
                <p className="mt-1 text-sm text-muted">
                  {address.recipient_name}, {address.line1}, {address.city}, {address.region}
                </p>
              </div>
              <ConfirmDialog
                title="Remove this address?"
                description="The address is deleted from your account. This does not affect any future order that has not been placed."
                confirmLabel="Remove"
                onConfirm={() => remove.mutate(address.id)}
              >
                <Button variant="danger" size="sm">
                  Remove
                </Button>
              </ConfirmDialog>
            </Card>
          ))}
        </div>
      )}
      <Card className="p-5">
        <h2 className="text-lg font-semibold text-navy">Add an address</h2>
        <form className="mt-4 grid gap-3 sm:grid-cols-2" onSubmit={form.handleSubmit((values) => create.mutate(values))}>
          <Field label="Label"><Input {...form.register("label")} /></Field>
          <Field label="Recipient"><Input {...form.register("recipient_name")} /></Field>
          <Field label="Address line" className="sm:col-span-2"><Input {...form.register("line1")} /></Field>
          <Field label="City"><Input {...form.register("city")} /></Field>
          <Field label="Region"><Input {...form.register("region")} /></Field>
          <Field label="Country"><Input {...form.register("country")} /></Field>
          <label className="flex items-center gap-2 text-sm text-navy sm:col-span-2">
            <input type="checkbox" {...form.register("is_default")} />
            Make this the default address
          </label>
          {create.isError ? (
            <p className="text-sm text-danger sm:col-span-2">
              {create.error instanceof MediSourceApiError ? create.error.message : "The address could not be saved."}
            </p>
          ) : null}
          <Button type="submit" disabled={create.isPending}>
            {create.isPending ? "Saving…" : "Save address"}
          </Button>
        </form>
      </Card>
    </div>
  );
}

function Field({ label, children, className }: { label: string; children: ReactNode; className?: string }) {
  return (
    <div className={className}>
      <Label>{label}</Label>
      <div className="mt-1.5">{children}</div>
    </div>
  );
}
