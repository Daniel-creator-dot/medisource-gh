import { PageHeader } from "@/components/page-header";

export function InfoPage({
  eyebrow,
  title,
  body,
  sections,
}: {
  eyebrow: string;
  title: string;
  body: string;
  sections: { heading: string; text: string }[];
}) {
  return (
    <>
      <PageHeader eyebrow={eyebrow} title={title} body={body} />
      <div className="mx-auto grid max-w-3xl gap-8 px-4 py-12">
        {sections.map((section) => (
          <section key={section.heading}>
            <h2 className="text-xl font-semibold text-navy">{section.heading}</h2>
            <p className="mt-2 text-sm leading-7 text-muted">{section.text}</p>
          </section>
        ))}
      </div>
    </>
  );
}
