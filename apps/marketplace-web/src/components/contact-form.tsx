"use client";

import { MediSourceApiError, apiRequest } from "@medisource/api-client";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button, Input, Label, Textarea } from "@medisource/ui";
import type { Envelope } from "@medisource/shared-types";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

const schema = z.object({
  name: z.string().min(2, "Enter your name."),
  email: z.email("Enter a valid email address."),
  organization_name: z.string().optional(),
  topic: z.enum(["general", "supplier", "facility", "support"]),
  message: z.string().min(20, "Write at least 20 characters.").max(2000),
});

export function ContactForm() {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", email: "", organization_name: "", topic: "general", message: "" },
  });

  return (
    <form
      className="grid gap-4"
      onSubmit={form.handleSubmit(async (values) => {
        setError(null);
        setMessage(null);
        try {
          const csrf = await apiRequest<Envelope<{ csrf_token: string }>>("/api/v1/auth/csrf/");
          await apiRequest<Envelope<{ received: boolean }>>("/api/v1/support/inquiries/", {
            method: "POST",
            body: values,
            csrfToken: csrf.data.csrf_token,
          });
          setMessage("Your message has been stored. A person will need to read it; there is no automated reply yet.");
          form.reset();
        } catch (caught) {
          setError(caught instanceof MediSourceApiError ? caught.message : "The message could not be sent.");
        }
      })}
    >
      <div className="grid gap-1.5">
        <Label htmlFor="name">Name</Label>
        <Input id="name" {...form.register("name")} />
        <FieldError message={form.formState.errors.name?.message} />
      </div>
      <div className="grid gap-1.5">
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" {...form.register("email")} />
        <FieldError message={form.formState.errors.email?.message} />
      </div>
      <div className="grid gap-1.5">
        <Label htmlFor="organization_name">Organization</Label>
        <Input id="organization_name" {...form.register("organization_name")} />
      </div>
      <div className="grid gap-1.5">
        <Label htmlFor="topic">Topic</Label>
        <select id="topic" className="h-11 rounded-xl border border-line bg-white px-3 text-sm" {...form.register("topic")}>
          <option value="general">General</option>
          <option value="supplier">Supplier</option>
          <option value="facility">Facility</option>
          <option value="support">Support</option>
        </select>
      </div>
      <div className="grid gap-1.5">
        <Label htmlFor="message">Message</Label>
        <Textarea id="message" {...form.register("message")} />
        <FieldError message={form.formState.errors.message?.message} />
      </div>
      {message ? <p className="text-sm text-success">{message}</p> : null}
      {error ? <p className="text-sm text-danger">{error}</p> : null}
      <Button type="submit" disabled={form.formState.isSubmitting}>
        {form.formState.isSubmitting ? "Sending…" : "Send message"}
      </Button>
    </form>
  );
}

function FieldError({ message }: { message?: string }) {
  if (!message) {
    return null;
  }
  return <p className="text-sm text-danger">{message}</p>;
}
