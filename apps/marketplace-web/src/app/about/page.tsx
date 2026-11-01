import type { Metadata } from "next";

import { InfoPage } from "@/components/info-page";

export const metadata: Metadata = { title: "About" };

export default function AboutPage() {
  return (
    <InfoPage
      eyebrow="About"
      title="A marketplace with explicit limits"
      body="MediSource GH is being built as one Django API and a set of web clients. The public site and customer account are the first working slice."
      sections={[
        {
          heading: "What is live",
          text: "Customers can register, manage addresses and notifications, and browse a database-backed catalogue. Category policy decides whether a future checkout may include a product. Sample suppliers and products are fictional.",
        },
        {
          heading: "What is next",
          text: "Supplier verification, orders, sandbox payments, professional credentials, appointment booking, and facility procurement are designed and not yet available in the interface.",
        },
        {
          heading: "Ghana first",
          text: "The first operating context is Ghana. Currency defaults to Ghana cedis, and the time zone is Africa/Accra. Regulatory approvals are prerequisites for production, not badges on this site.",
        },
      ]}
    />
  );
}
