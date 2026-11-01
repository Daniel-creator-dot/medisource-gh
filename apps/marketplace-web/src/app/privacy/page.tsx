import type { Metadata } from "next";

import { InfoPage } from "@/components/info-page";

export const metadata: Metadata = { title: "Privacy" };

export default function PrivacyPage() {
  return (
    <InfoPage
      eyebrow="Privacy"
      title="What this release stores"
      body="This notice describes the development application. It is not a registration with the Data Protection Commission and it is not legal advice."
      sections={[
        {
          heading: "Account data",
          text: "Registration stores your name, email, optional phone, and a password hash. Addresses are stored only if you add them. Sign-in events are written to the audit log. If you enable an authenticator, the secret is encrypted at rest.",
        },
        {
          heading: "Messages",
          text: "The contact form stores your name, email, optional organization, topic, and message so a person can reply. There is no mailing list.",
        },
        {
          heading: "What is not collected",
          text: "This release does not collect clinical records, prescriptions, payment card numbers, or Mobile Money credentials. Catalogue sample data is fictional.",
        },
      ]}
    />
  );
}
