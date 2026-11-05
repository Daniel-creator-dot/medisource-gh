import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4">
      <p className="text-sm font-semibold tracking-wide text-[var(--orange)]">SRAJ NOVA</p>
      <h1 className="mt-2 text-3xl font-semibold text-[var(--navy)]">Agency command center</h1>
      <p className="mt-3 text-sm text-[var(--muted)]">
        SRAJ NOVA is the workforce agency. The sample factories are client organizations. This sign-in uses demonstration accounts.
      </p>
      <div className="mt-6 rounded-lg border border-[var(--line)] bg-[var(--card)] p-5">
        <LoginForm />
      </div>
    </main>
  );
}
