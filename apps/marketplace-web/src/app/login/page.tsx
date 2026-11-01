import type { Metadata } from "next";

import { AuthLink, AuthShell } from "@/components/auth-shell";
import { LoginForm } from "@/components/auth-forms";

export const metadata: Metadata = { title: "Sign in" };

export default function LoginPage() {
  return (
    <AuthShell
      title="Sign in"
      body="Customer accounts use an HttpOnly cookie. Privileged accounts may be asked for an authenticator code before a session is issued."
      footer={
        <>
          New to MediSource? <AuthLink href="/register">Create an account</AuthLink>.{" "}
          <AuthLink href="/forgot-password">Forgot password</AuthLink>
        </>
      }
    >
      <LoginForm />
    </AuthShell>
  );
}
