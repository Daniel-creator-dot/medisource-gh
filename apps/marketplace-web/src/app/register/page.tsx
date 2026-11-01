import type { Metadata } from "next";

import { RegisterForm } from "@/components/auth-forms";
import { AuthLink, AuthShell } from "@/components/auth-shell";

export const metadata: Metadata = { title: "Create account" };

export default function RegisterPage() {
  return (
    <AuthShell
      title="Create a customer account"
      body="Registration creates a customer. It cannot assign an administrator, supplier, or facility role. Supplier onboarding is a later release."
      footer={
        <>
          Already registered? <AuthLink href="/login">Sign in</AuthLink>
        </>
      }
    >
      <RegisterForm />
    </AuthShell>
  );
}
