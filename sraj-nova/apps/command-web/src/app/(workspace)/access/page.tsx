import { RoleForm } from "@/components/account-controls";
import { apiGet } from "@/lib/api";

type Account = {
  id: string;
  email: string;
  name: string;
  role: string;
  role_label: string;
  client_name: string | null;
  employee_number: string | null;
  assignable_roles: { value: string; label: string }[];
  mfa_enabled: boolean;
  is_demo: boolean;
};

export default async function AccessPage() {
  const result = await apiGet<Account[]>("/auth/users/");
  return (
    <>
      <p className="text-sm font-semibold tracking-[0.14em] text-[var(--muted)]">ROLES</p>
      <h1 className="display mt-1 text-4xl font-bold">Roles</h1>
      <p className="mt-1 max-w-3xl text-sm text-[var(--muted)]">
        The agency owner can change a role when the account is linked for it. A client user needs one client. An employee needs a worker record. The last agency owner cannot be removed.
      </p>
      {result.status === 403 ? <p className="mt-3">{result.message}</p> : null}
      <div className="sheet mt-4">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-[var(--line)] text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">Email</th>
              <th className="px-3 py-2 font-medium">Linked to</th>
              <th className="px-3 py-2 font-medium">Role</th>
            </tr>
          </thead>
          <tbody>
            {(result.data ?? []).map((user) => (
              <tr key={user.id} className="border-b border-[var(--line)]">
                <td className="px-3 py-2">{user.name}</td>
                <td className="px-3 py-2">{user.email}</td>
                <td className="px-3 py-2 text-[var(--muted)]">{user.client_name || user.employee_number || "Whole agency"}</td>
                <td className="px-3 py-2">
                  <RoleForm userId={user.id} role={user.role} choices={user.assignable_roles} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
