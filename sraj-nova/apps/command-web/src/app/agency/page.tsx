import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Agency = {
  legal_name: string;
  trading_name: string;
  country: string;
  currency: string;
  timezone: string;
  role: string;
};

export default async function AgencyPage() {
  const result = await apiGet<Agency>("/agency/");
  return (
    <Shell>
      <h1 className="display text-4xl font-bold">Agency</h1>
      {result.status === 403 || !result.data ? (
        <p className="mt-3">{result.message || "Agency configuration is limited to agency staff."}</p>
      ) : (
        <dl className="panel mt-4 grid max-w-xl gap-3 p-4 text-sm">
          <div><dt className="text-[var(--muted)]">Legal name</dt><dd>{result.data.legal_name}</dd></div>
          <div><dt className="text-[var(--muted)]">Trading name</dt><dd>{result.data.trading_name}</dd></div>
          <div><dt className="text-[var(--muted)]">Country</dt><dd>{result.data.country}</dd></div>
          <div><dt className="text-[var(--muted)]">Currency</dt><dd>{result.data.currency}</dd></div>
          <div><dt className="text-[var(--muted)]">Timezone</dt><dd>{result.data.timezone}</dd></div>
          <div><dt className="text-[var(--muted)]">Operating role</dt><dd>{result.data.role}</dd></div>
        </dl>
      )}
    </Shell>
  );
}
