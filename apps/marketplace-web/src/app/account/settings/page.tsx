"use client";

import { MediSourceApiError } from "@medisource/api-client";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button, Input, Label } from "@medisource/ui";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { browserApi } from "@/lib/browser-api";

const schema = z.object({
  first_name: z.string().min(1, "Enter your first name."),
  last_name: z.string().min(1, "Enter your last name."),
  phone_number: z.string().max(20),
});

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const me = useQuery({ queryKey: ["me"], queryFn: () => browserApi.me() });
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { first_name: "", last_name: "", phone_number: "" },
  });
  useEffect(() => {
    if (me.data) {
      form.reset({
        first_name: me.data.data.first_name,
        last_name: me.data.data.last_name,
        phone_number: me.data.data.phone_number,
      });
    }
  }, [me.data, form]);

  const mutation = useMutation({
    mutationFn: (values: z.infer<typeof schema>) => browserApi.updateMe(values),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  return (
    <div className="max-w-lg">
      <h1 className="text-3xl font-semibold text-navy">Settings</h1>
      <p className="mt-2 text-sm text-muted">Email and role cannot be changed from this form.</p>
      <form className="mt-6 grid gap-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
        <div className="grid gap-1.5">
          <Label htmlFor="first_name">First name</Label>
          <Input id="first_name" {...form.register("first_name")} />
        </div>
        <div className="grid gap-1.5">
          <Label htmlFor="last_name">Last name</Label>
          <Input id="last_name" {...form.register("last_name")} />
        </div>
        <div className="grid gap-1.5">
          <Label htmlFor="phone_number">Phone</Label>
          <Input id="phone_number" {...form.register("phone_number")} />
        </div>
        {mutation.isError ? (
          <p className="text-sm text-danger">
            {mutation.error instanceof MediSourceApiError ? mutation.error.message : "The profile could not be saved."}
          </p>
        ) : null}
        {mutation.isSuccess ? <p className="text-sm text-success">Profile saved.</p> : null}
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Saving…" : "Save profile"}
        </Button>
      </form>
    </div>
  );
}
