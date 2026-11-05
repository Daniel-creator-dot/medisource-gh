import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type ClientDetail = {
  legal_name: string;
  sector: string;
  demo_label: string;
  sites: { id: string; name: string; city: string; region: string; departments: string[] }[];
};

export default async function ClientPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const result = await apiGet<ClientDetail>(`/clients/${slug}/`);
  return (
    <Shell>
      {result.status === 404 || !result.data ? (
        <h1 className="text-2xl font-semibold">Client not available</h1>
      ) : (
        <>
          <h1 className="text-2xl font-semibold">{result.data.legal_name}</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            {result.data.sector}. {result.data.demo_label}
          </p>
          <ul className="mt-6 space-y-3">
            {result.data.sites.map((site) => (
              <li key={site.id} className="rounded-lg border border-[var(--line)] bg-[var(--card)] p-4">
                <p className="font-medium">{site.name}</p>
                <p className="text-sm text-[var(--muted)]">
                  {site.city}, {site.region}
                </p>
                <p className="mt-2 text-sm">Departments: {site.departments.join(", ")}</p>
              </li>
            ))}
          </ul>
        </>
      )}
    </Shell>
  );
}
