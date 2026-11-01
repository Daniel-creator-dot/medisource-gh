import type { Metadata } from "next";

import { InfoPage } from "@/components/info-page";

export const metadata: Metadata = { title: "Terms" };

export default function TermsPage() {
  return (
    <InfoPage
      eyebrow="Terms"
      title="Development terms"
      body="This environment is for building and demonstrating MediSource GH. It is not a live marketplace and it does not sell products."
      sections={[
        {
          heading: "Sample records",
          text: "Suppliers, products, and demo accounts marked Sample are fictional. They are not offers, approvals, or verified businesses. Purchase is blocked in the API.",
        },
        {
          heading: "Accounts",
          text: "You are responsible for the password on any account you create. Privileged roles, when MFA is required, cannot receive a session until an authenticator is enrolled.",
        },
        {
          heading: "No clinical service",
          text: "Nothing on this site is medical advice, a prescription, or a booking with a clinician. Professional and facility services are not available yet.",
        },
      ]}
    />
  );
}
