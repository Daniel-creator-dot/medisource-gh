import type { Metadata } from "next";

import { ForgotPasswordForm } from "@/components/auth-forms";
import { AuthLink, AuthShell } from "@/components/auth-shell";

export const metadata: Metadata = { title: "Reset password" };

export default function ForgotPasswordPage() {
  return (
    <AuthShell
      title="Reset your password"
      body="If the email matches an account, the reset link is printed by the local mail console. The page always shows the same confirmation."
      footer={
        <>
          Back to <AuthLink href="/login">sign in</AuthLink>
        </>
      }
    >
      <ForgotPasswordForm />
    </AuthShell>
  );
}
