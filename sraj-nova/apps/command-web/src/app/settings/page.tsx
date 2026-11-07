import { PasswordForm, SignOutButton } from "@/components/account-controls";
import { Shell } from "@/components/shell";
import { apiGet } from "@/lib/api";
import Link from "next/link";

type Settings = {
  email: string;
  name: string;
  role: string;
  role_label: string;
  opens: string[];
  mfa_enabled: boolean;
  mfa_required_for_owner: boolean;
  late_grace_minutes: number;
  min_rest_hours: number;
  can_manage_roles: boolean;
  can_manage_hr: boolean;
};

export default async function SettingsPage() {
  const result = await apiGet<Settings>("/auth/settings/");
  const settings = result.data;
  if (!settings) {
    return (
      <Shell>
        <h1 className="display text-4xl font-bold">Settings</h1>
        <p className="mt-3">{result.message || "This account cannot open settings."}</p>
      </Shell>
    );
  }
  return (
    <Shell>
      <p className="text-sm font-semibold tracking-[0.14em] text-[var(--muted)]">ACCOUNT</p>
      <h1 className="display mt-1 text-4xl font-bold">Settings</h1>
      <nav className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Link className="panel p-4" href="/settings"><p className="text-sm text-[var(--muted)]">Account</p><p className="mt-1 font-semibold">Password and sign-in</p></Link>
        <Link className="panel p-4" href="/access"><p className="text-sm text-[var(--muted)]">Roles</p><p className="mt-1 font-semibold">Who can open which screens</p></Link>
        {settings.can_manage_hr ? <Link className="panel p-4" href="/hr"><p className="text-sm text-[var(--muted)]">HR</p><p className="mt-1 font-semibold">Add staff to a department</p></Link> : null}
        {settings.can_manage_hr ? <Link className="panel p-4" href="/recruitment"><p className="text-sm text-[var(--muted)]">Recruitment</p><p className="mt-1 font-semibold">Applications and hiring</p></Link> : null}
        <Link className="panel p-4" href="/settings/tax"><p className="text-sm text-[var(--muted)]">Tax</p><p className="mt-1 font-semibold">PAYE and pension status</p></Link>
        <Link className="panel p-4" href="/settings"><p className="text-sm text-[var(--muted)]">Attendance</p><p className="mt-1 font-semibold">Late mark and rest hours</p></Link>
      </nav>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <article className="panel p-5">
          <h2 className="text-lg font-semibold">{settings.name}</h2>
          <p className="mt-1 text-sm text-[var(--muted)]">{settings.email}</p>
          <p className="mt-3 text-sm">Role: {settings.role_label}</p>
          <p className="mt-2 text-sm text-[var(--muted)]">This role opens {settings.opens.join(", ")}.</p>
          <p className="mt-3 text-sm">Authenticator: {settings.mfa_enabled ? "Enrolled" : "Not enrolled"}.</p>
          <p className="mt-1 text-sm text-[var(--muted)]">
            {settings.mfa_required_for_owner
              ? "An agency owner must enroll an authenticator before sign-in."
              : "This workspace does not require an authenticator before sign-in."}
          </p>
          <div className="mt-4">
            <SignOutButton />
          </div>
        </article>
        <article className="panel p-5">
          <h2 className="text-lg font-semibold">Password</h2>
          <p className="mt-1 text-sm text-[var(--muted)]">The current password is checked before the new one is stored. Use at least 8 characters.</p>
          <PasswordForm />
        </article>
        <article className="panel p-5">
          <h2 className="text-lg font-semibold">Floor rules</h2>
          <p className="mt-2 text-sm">A late mark is an arrival more than {settings.late_grace_minutes} minutes after the shift starts.</p>
          <p className="mt-2 text-sm">A worker needs {settings.min_rest_hours} hours between shifts before coverage will offer the next post.</p>
          <p className="mt-2 text-sm text-[var(--muted)]">These are the rules the attendance and coverage checks use.</p>
        </article>
        <article className="panel p-5">
          <h2 className="text-lg font-semibold">Roles</h2>
          <p className="mt-2 text-sm text-[var(--muted)]">
            The five roles are agency owner, agency operations, agency finance, client user, and employee. A client user stays on one plant. An employee sees only their own record. Agency finance can open the books. There is no separate payroll approver yet.
          </p>
          {settings.can_manage_roles ? (
            <Link className="mt-3 inline-flex text-sm font-semibold text-[var(--blue)]" href="/access">Assign roles</Link>
          ) : (
            <p className="mt-3 text-sm">Only the agency owner can change an account&apos;s role.</p>
          )}
        </article>
      </div>
    </Shell>
  );
}
