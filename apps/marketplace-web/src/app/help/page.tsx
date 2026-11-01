import type { Metadata } from "next";

import { InfoPage } from "@/components/info-page";

export const metadata: Metadata = { title: "Help" };

export default function HelpPage() {
  return (
    <InfoPage
      eyebrow="Help"
      title="Using this development release"
      body="If a page says the catalogue is unavailable, the Django API is not running or the browser cannot reach it."
      sections={[
        {
          heading: "Accounts",
          text: "Create a customer account from Register. In local development, the verification email is printed in the Django console. Password reset uses the same mailbox and always shows the same confirmation, whether or not the email exists.",
        },
        {
          heading: "Sample data",
          text: "Run the seed command to load fictional suppliers and products. They are marked Sample. Checkout is intentionally unavailable for them.",
        },
        {
          heading: "Support",
          text: "Use the contact form for a message stored on the platform. There is no live support desk behind it yet.",
        },
      ]}
    />
  );
}
