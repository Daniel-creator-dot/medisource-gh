import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";

type Account = { id: string; email: string; name: string; role: string; mfa_enabled: boolean; is_demo: boolean };

export default async function AccessPage() {
  const result = await apiGet<Account[]>("/auth/users/");
  return (
    <Shell>
      <h1 className="text-2xl font-semibold">Access</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">Agency owners can review accounts. This screen does not change roles or reset passwords.</p>
      {result.status === 403 ? <p className="mt-3">{result.message}</p> : null}
      <div className="mt-4 overflow-x-auto rounded-lg border border-[var(--line)] bg-[var(--card)]">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-[var(--line)] text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">Email</th>
              <th className="px-3 py-2 font-medium">Role</th>
              <th className="px-3 py-2 font-medium">Authenticator</th>
            </tr>
          </thead>
          <tbody>
            {(result.data ?? []).map((user) => (
              <tr key={user.id} className="border-b border-[var(--line)]">
                <td className="px-3 py-2">{user.name}</td>
                <td className="px-3 py-2">{user.email}</td>
                <td className="px-3 py-2">{user.role}</td>
                <td className="px-3 py-2">{user.mfa_enabled ? "Enabled" : "Not enrolled"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Shell>
  );
}
