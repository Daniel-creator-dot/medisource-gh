import type { Metadata } from "next";

import { InfoPage } from "@/components/info-page";

export const metadata: Metadata = { title: "Appointments" };

export default function AppointmentsPage() {
  return (
    <InfoPage
      eyebrow="Appointments"
      title="Booking is not open"
      body="You cannot reserve a clinician from this site yet. The booking engine will be a real transaction, not a form that only looks scheduled."
      sections={[
        {
          heading: "The intended path",
          text: "A customer chooses a verified professional, an allowed service, a place or remote mode, and an open slot. The API holds the slot inside a database transaction. A second booking of the same range is rejected by a PostgreSQL exclusion constraint.",
        },
        {
          heading: "Payment and changes",
          text: "Confirmation will depend on the payment or facility guarantee, not on the browser returning from a gateway. Cancellation and rescheduling will follow the policy stored on the service.",
        },
      ]}
    />
  );
}
