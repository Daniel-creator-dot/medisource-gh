"use client";

import { MediSourceApiError } from "@medisource/api-client";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button, Input, Label } from "@medisource/ui";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { browserApi } from "@/lib/browser-api";

const credentials = z.object({
  email: z.email("Enter a valid email address."),
  password: z.string().min(12, "Use at least 12 characters."),
});

const registration = credentials.extend({
  first_name: z.string().min(1, "Enter your first name."),
  last_name: z.string().min(1, "Enter your last name."),
  phone_number: z.string().max(20).optional(),
});

export function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const form = useForm<z.infer<typeof credentials>>({
    resolver: zodResolver(credentials),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: z.infer<typeof credentials>) {
    setError(null);
    try {
      const result = await browserApi.login(values.email, values.password);
      if (result.data.mfa_required && result.data.mfa_token) {
        setMfaToken(result.data.mfa_token);
        return;
      }
      router.push("/account/dashboard");
      router.refresh();
    } catch (caught) {
      setError(caught instanceof MediSourceApiError ? caught.message : "Sign-in failed.");
    }
  }

  async function verifyMfa() {
    if (!mfaToken) {
      return;
    }
    setError(null);
    try {
      await browserApi.verifyMfa(mfaToken, code);
      router.push("/account/dashboard");
      router.refresh();
    } catch (caught) {
      setError(caught instanceof MediSourceApiError ? caught.message : "The code was not accepted.");
    }
  }

  if (mfaToken) {
    return (
      <form
        className="grid gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          void verifyMfa();
        }}
      >
        <Field label="Authenticator code">
          <Input value={code} onChange={(event) => setCode(event.target.value)} inputMode="numeric" autoComplete="one-time-code" required />
        </Field>
        {error ? <p className="text-sm text-danger">{error}</p> : null}
        <Button type="submit">Confirm code</Button>
      </form>
    );
  }

  return (
    <form className="grid gap-4" onSubmit={form.handleSubmit(onSubmit)}>
      <Field label="Email" error={form.formState.errors.email?.message}>
        <Input type="email" autoComplete="email" {...form.register("email")} />
      </Field>
      <Field label="Password" error={form.formState.errors.password?.message}>
        <Input type="password" autoComplete="current-password" {...form.register("password")} />
      </Field>
      {error ? <p className="text-sm text-danger">{error}</p> : null}
      <Button type="submit" disabled={form.formState.isSubmitting}>
        {form.formState.isSubmitting ? "Signing in…" : "Sign in"}
      </Button>
    </form>
  );
}

export function RegisterForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const form = useForm<z.infer<typeof registration>>({
    resolver: zodResolver(registration),
    defaultValues: { email: "", password: "", first_name: "", last_name: "", phone_number: "" },
  });

  async function onSubmit(values: z.infer<typeof registration>) {
    setError(null);
    try {
      await browserApi.register(values);
      router.push("/account/dashboard");
      router.refresh();
    } catch (caught) {
      setError(caught instanceof MediSourceApiError ? caught.message : "Registration failed.");
    }
  }

  return (
    <form className="grid gap-4" onSubmit={form.handleSubmit(onSubmit)}>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="First name" error={form.formState.errors.first_name?.message}>
          <Input autoComplete="given-name" {...form.register("first_name")} />
        </Field>
        <Field label="Last name" error={form.formState.errors.last_name?.message}>
          <Input autoComplete="family-name" {...form.register("last_name")} />
        </Field>
      </div>
      <Field label="Email" error={form.formState.errors.email?.message}>
        <Input type="email" autoComplete="email" {...form.register("email")} />
      </Field>
      <Field label="Phone" error={form.formState.errors.phone_number?.message}>
        <Input autoComplete="tel" {...form.register("phone_number")} />
      </Field>
      <Field label="Password" error={form.formState.errors.password?.message}>
        <Input type="password" autoComplete="new-password" {...form.register("password")} />
      </Field>
      {error ? <p className="text-sm text-danger">{error}</p> : null}
      <Button type="submit" disabled={form.formState.isSubmitting}>
        {form.formState.isSubmitting ? "Creating account…" : "Create account"}
      </Button>
    </form>
  );
}

const emailOnly = z.object({ email: z.email("Enter a valid email address.") });
const resetPassword = z.object({
  password: z.string().min(12, "Use at least 12 characters."),
});

export function ForgotPasswordForm() {
  const params = useSearchParams();
  const token = params.get("token");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const requestForm = useForm<z.infer<typeof emailOnly>>({
    resolver: zodResolver(emailOnly),
    defaultValues: { email: "" },
  });
  const resetForm = useForm<z.infer<typeof resetPassword>>({
    resolver: zodResolver(resetPassword),
    defaultValues: { password: "" },
  });

  if (token) {
    return (
      <form
        className="grid gap-4"
        onSubmit={resetForm.handleSubmit(async (values) => {
          setError(null);
          try {
            await browserApi.confirmPasswordReset(token, values.password);
            setMessage("Your password has been updated. You can sign in.");
          } catch (caught) {
            setError(caught instanceof MediSourceApiError ? caught.message : "The reset link could not be used.");
          }
        })}
      >
        <Field label="New password" error={resetForm.formState.errors.password?.message}>
          <Input type="password" autoComplete="new-password" {...resetForm.register("password")} />
        </Field>
        {message ? <p className="text-sm text-success">{message}</p> : null}
        {error ? <p className="text-sm text-danger">{error}</p> : null}
        <Button type="submit">Update password</Button>
      </form>
    );
  }

  return (
    <form
      className="grid gap-4"
      onSubmit={requestForm.handleSubmit(async (values) => {
        setError(null);
        try {
          const result = await browserApi.requestPasswordReset(values.email);
          setMessage(result.data.message);
        } catch (caught) {
          setError(caught instanceof MediSourceApiError ? caught.message : "The request could not be sent.");
        }
      })}
    >
      <Field label="Email" error={requestForm.formState.errors.email?.message}>
        <Input type="email" autoComplete="email" {...requestForm.register("email")} />
      </Field>
      {message ? <p className="text-sm text-navy">{message}</p> : null}
      {error ? <p className="text-sm text-danger">{error}</p> : null}
      <Button type="submit">Send reset link</Button>
    </form>
  );
}

export function VerifyAccountButton() {
  const params = useSearchParams();
  const token = params.get("token");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function verify() {
    if (!token) {
      setError("Open the verification link from your email.");
      return;
    }
    setError(null);
    try {
      await browserApi.verifyEmail(token);
      setMessage("Your email is verified. You can continue to your account.");
    } catch (caught) {
      setError(caught instanceof MediSourceApiError ? caught.message : "Verification failed.");
    }
  }

  return (
    <div className="grid gap-4">
      <Button onClick={() => void verify()}>Confirm email</Button>
      {message ? <p className="text-sm text-success">{message}</p> : null}
      {error ? <p className="text-sm text-danger">{error}</p> : null}
    </div>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div className="grid gap-1.5">
      <Label>{label}</Label>
      {children}
      {error ? <p className="text-sm text-danger">{error}</p> : null}
    </div>
  );
}
