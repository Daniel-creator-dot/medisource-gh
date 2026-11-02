import { MediSourceApiError } from "@medisource/api-client";
import { Card } from "@medisource/ui";
import type { Metadata } from "next";
import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import { EmptyState, ErrorState } from "@/components/states";
import { getProfessionals, getProfessionRoles } from "@/lib/catalog";
import { firstParam } from "@/lib/format";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Professionals" };

export default async function ProfessionalsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const q = firstParam(params.q) ?? "";
  const role = firstParam(params.role) ?? "";
  const region = firstParam(params.region) ?? "";

  let directory: Awaited<ReturnType<typeof getProfessionRoles>>["data"] | null = null;
  let professionals: Awaited<ReturnType<typeof getProfessionals>>["data"] | null = null;
  let errorMessage: string | null = null;
  try {
    const [roles, people] = await Promise.all([getProfessionRoles(), getProfessionals({ q, role, region })]);
    directory = roles.data;
    professionals = people.data;
  } catch (error) {
    errorMessage = error instanceof MediSourceApiError ? error.message : "The directory could not be loaded.";
  }
  if (errorMessage || !directory || !professionals) {
    return (
      <>
        <PageHeader eyebrow="Professionals" title="Healthcare professional directory" body="Profiles are loaded from the API." />
        <div className="mx-auto max-w-6xl px-4 py-10">
          <ErrorState title="Directory unavailable" body={errorMessage ?? "The directory could not be loaded."} />
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Professionals"
        title="Healthcare professional directory"
        body={directory.notice}
      />
      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {directory.roles.map((item) => (
            <Link key={item.id} href={`/professionals?role=${item.slug}`} className="rounded-2xl border border-line bg-white p-4 hover:border-teal">
              <h2 className="font-semibold text-navy">{item.name}</h2>
              <p className="mt-2 text-sm leading-6 text-muted">{item.description}</p>
            </Link>
          ))}
        </div>
        <form action="/professionals" className="mt-8 grid gap-3 rounded-2xl border border-line bg-white p-4 md:grid-cols-[1fr_200px_200px_auto]">
          <input
            name="q"
            defaultValue={q}
            placeholder="Search by name or city"
            aria-label="Search professionals"
            className="h-12 rounded-full border border-line px-5 text-sm outline-none focus-visible:ring-2 focus-visible:ring-teal"
          />
          <select name="role" defaultValue={role} aria-label="Profession" className="h-12 rounded-full border border-line bg-white px-4 text-sm">
            <option value="">All professions</option>
            {directory.roles.map((item) => (
              <option key={item.id} value={item.slug}>
                {item.name}
              </option>
            ))}
          </select>
          <select name="region" defaultValue={region} aria-label="Region" className="h-12 rounded-full border border-line bg-white px-4 text-sm">
            <option value="">All regions</option>
            {directory.regions.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
          <button type="submit" className="h-12 rounded-full bg-navy px-5 text-sm font-semibold text-white">
            Apply
          </button>
        </form>
        {professionals.length === 0 ? (
          <div className="mt-8">
            <EmptyState
              title="No verified professionals"
              body="MediSource does not publish sample doctors, nurses, or other clinicians. A profile appears here only after a reviewer accepts a current credential."
            />
          </div>
        ) : (
          <ul className="mt-8 grid gap-4 md:grid-cols-2">
            {professionals.map((person) => (
              <li key={person.id}>
                <Card className="p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal-dark">{person.role_name}</p>
                  <h2 className="mt-2 text-xl font-semibold text-navy">{person.display_name}</h2>
                  <p className="mt-1 text-sm text-muted">
                    {person.city}, {person.region}
                  </p>
                  <p className="mt-3 text-sm leading-6 text-ink">{person.summary}</p>
                  <p className="mt-3 text-xs text-muted">Credential current through {person.credential_expires_on}</p>
                </Card>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}
