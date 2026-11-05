"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

const schema = z.object({
  email: z.email("Enter a valid email."),
  password: z.string().min(1, "Enter the demonstration password."),
});

type FormValues = z.infer<typeof schema>;

async function csrfToken() {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "include", cache: "reload" });
  const body = (await response.json()) as { data: { csrf_token: string } };
  return body.data.csrf_token;
}

export function LoginForm() {
  const router = useRouter();
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "nova.owner@sample.sraj.test", password: "Demo-Only-Change-Me-1" },
  });
  const login = useMutation({
    mutationFn: async (values: FormValues) => {
      const token = await csrfToken();
      const response = await fetch("/api/v1/auth/login/", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRFToken": token },
        body: JSON.stringify(values),
      });
      const body = (await response.json()) as { error?: { message: string }; data?: { user?: { role: string } } };
      if (!response.ok) throw new Error(body.error?.message || "Sign-in failed.");
      return body.data?.user?.role;
    },
    onSuccess: (role) => router.push(role === "employee" ? "/me" : "/command"),
  });

  return (
    <form className="space-y-4" onSubmit={form.handleSubmit((values) => login.mutate(values))} noValidate>
      <label className="block text-sm font-medium" htmlFor="email">
        Email
        <input id="email" type="email" className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" {...form.register("email")} />
      </label>
      {form.formState.errors.email ? <p className="text-sm text-red-700">{form.formState.errors.email.message}</p> : null}
      <label className="block text-sm font-medium" htmlFor="password">
        Password
        <input id="password" type="password" className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--canvas)] px-3 py-2" {...form.register("password")} />
      </label>
      {login.error ? <p className="text-sm text-red-700">{login.error.message}</p> : null}
      <button type="submit" disabled={login.isPending} className="w-full rounded-full bg-[var(--orange)] px-4 py-2.5 font-semibold text-white disabled:opacity-60">
        {login.isPending ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
