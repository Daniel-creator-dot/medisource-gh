import type { Metadata } from "next";

import { InfoPage } from "@/components/info-page";

export const metadata: Metadata = { title: "Facilities" };

export default function FacilitiesPage() {
  return (
    <InfoPage
      eyebrow="Facilities"
      title="Facility directory comes with procurement"
      body="Hospitals, clinics, pharmacies, and laboratories will have their own organizations, departments, and staff roles. That portal is not open in this release, so there is no invented facility list."
      sections={[
        {
          heading: "Isolation",
          text: "A facility member will see that facility's requisitions and orders. Another facility's records return as not found, the same pattern already used for supplier notes and customer addresses.",
        },
        {
          heading: "Approvals",
          text: "Thresholds and roles will decide who can approve a requisition. A requester will not be able to approve their own request above the self-approval limit.",
        },
      ]}
    />
  );
}
