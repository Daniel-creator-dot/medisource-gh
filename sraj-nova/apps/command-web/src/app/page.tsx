import { LoginForm } from "@/components/login-form";
import { Mark } from "@/components/mark";

export default function LoginPage() {
  return (
    <main className="grid min-h-screen lg:grid-cols-[1.1fr_0.9fr]">
      <section className="relative flex min-h-[42vh] flex-col justify-between overflow-hidden bg-[#0b1f33] px-6 py-8 text-white sm:px-10">
        <div className="hero-grid absolute inset-0" />
        <div className="relative">
          <Mark light />
          <p className="display mt-10 max-w-xl text-5xl font-bold leading-none sm:text-6xl">Workforce command for every client site.</p>
          <p className="mt-4 max-w-md text-white/75">
            SRAJ NOVA recruits, deploys, and pays workers assigned to external factories. This sign-in uses demonstration accounts.
          </p>
        </div>
        <p className="relative mt-10 text-sm text-white/55">GHS · Africa/Accra · Sample data</p>
      </section>
      <section className="flex items-center px-6 py-12">
        <div className="mx-auto w-full max-w-md">
          <p className="text-sm font-semibold tracking-[0.16em] text-[var(--orange)]">AGENCY ACCESS</p>
          <h1 className="display mt-2 text-4xl font-bold">Sign in</h1>
          <div className="panel mt-6 p-5">
            <LoginForm />
          </div>
        </div>
      </section>
    </main>
  );
}
