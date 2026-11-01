import type { Metadata } from "next";

import { VerifyAccountButton } from "@/components/auth-forms";
import { AuthShell } from "@/components/auth-shell";

export const metadata: Metadata = { title: "Verify email" };

export default function VerifyAccountPage() {
  return (
    <AuthShell
      title="Verify your email"
      body="Use the link from the verification message, then confirm it here. The button avoids consuming the token twice during page load."
    >
      <VerifyAccountButton />
    </AuthShell>
  );
}
