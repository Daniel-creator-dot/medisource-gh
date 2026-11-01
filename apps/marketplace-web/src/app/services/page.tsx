import type { Metadata } from "next";

import { InfoPage } from "@/components/info-page";

export const metadata: Metadata = { title: "Services" };

export default function ServicesPage() {
  return (
    <InfoPage
      eyebrow="Services"
      title="Services follow the catalogue and, later, credentials"
      body="Today the live service is product discovery. Home care, diagnostics booking, and consultations are not offered."
      sections={[
        {
          heading: "Products",
          text: "Eligible consumables, equipment, instruments, laboratory supplies, diagnostics, furniture, PPE, orthopedic supplies, and rehabilitation equipment can be browsed. Authorized pharmaceuticals remain visible as a closed category.",
        },
        {
          heading: "Care services",
          text: "A professional service will be bookable only when the matching credential is current. MediSource will not add a diagnosis, prescription, or automated clinical approval.",
        },
      ]}
    />
  );
}
