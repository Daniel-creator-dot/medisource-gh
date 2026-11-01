import type { Metadata } from "next";

import { ContactForm } from "@/components/contact-form";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Contact" };

export default function ContactPage() {
  return (
    <>
      <PageHeader
        eyebrow="Contact"
        title="Send a message"
        body="The form stores an inquiry in the database. It does not open a live chat or create a supplier account."
      />
      <div className="mx-auto max-w-xl px-4 py-10">
        <ContactForm />
      </div>
    </>
  );
}
