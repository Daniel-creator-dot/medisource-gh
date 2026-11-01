import type { Metadata } from "next";

import { InfoPage } from "@/components/info-page";

export const metadata: Metadata = { title: "Professionals" };

export default function ProfessionalsPage() {
  return (
    <InfoPage
      eyebrow="Professionals"
      title="No clinicians are listed yet"
      body="MediSource will not publish a doctor, nurse, midwife, pharmacist, or allied professional until a reviewer accepts their credential. This page does not use sample people, because a fictional licence looks like a real one."
      sections={[
        {
          heading: "Verification",
          text: "Uploading a certificate will create a review item. It will not flip the profile to verified. A platform administrator records the decision, and that decision is audited.",
        },
        {
          heading: "Expiry and suspension",
          text: "When booking exists, an expired or suspended credential will remove the services that depend on it. Existing appointments will be flagged for a person to resolve.",
        },
        {
          heading: "Who can be included later",
          text: "Doctors, specialists, nurses, midwives, physiotherapists, pharmacists, dietitians, qualified mental health professionals, and other eligible allied roles, each matched to the council that actually regulates them.",
        },
      ]}
    />
  );
}
