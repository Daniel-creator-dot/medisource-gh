import Link from "next/link";

import { apiGet } from "@/lib/api";

type ClientRow = {
  id: string;
  legal_name: string;
  slug: string;
  sector: string;
  site_count: number;
  deployed_workers: number;
  is_demo: boolean;
  demo_label: string;
};

export default async function ClientsPage() {
  const result = await apiGet<ClientRow[]>("/clients/");
  return (
    <>
      <p className="text-sm font-semibold tracking-[0.16em] text-[var(--orange)]">CLIENTS</p>
      <h1 className="display mt-1 text-4xl font-bold">Client organizations</h1>
      {result.status === 403 ? <p className="mt-3">{result.message}</p> : null}
      <div className="sheet mt-4">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-[var(--line)] text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2 font-medium">Client</th>
              <th className="px-3 py-2 font-medium">Sector</th>
              <th className="px-3 py-2 font-medium">Sites</th>
              <th className="px-3 py-2 font-medium">Deployed</th>
            </tr>
          </thead>
          <tbody>
            {(result.data ?? []).map((client) => (
              <tr key={client.id} className="border-b border-[var(--line)]">
                <td className="px-3 py-2">
                  <Link href={`/clients/${client.slug}`} className="font-medium underline">
                    {client.legal_name}
                  </Link>
                  {client.is_demo ? <p className="text-xs text-[var(--muted)]">{client.demo_label}</p> : null}
                </td>
                <td className="px-3 py-2">{client.sector}</td>
                <td className="px-3 py-2">{client.site_count}</td>
                <td className="px-3 py-2">{client.deployed_workers}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
