import Link from "next/link";

export function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2.5 rounded-lg">
      <span className="grid h-9 w-9 place-items-center rounded-xl bg-navy text-care" aria-hidden="true">
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2.2">
          <path d="M12 4v16M4 12h16" strokeLinecap="round" />
        </svg>
      </span>
      <span>
        <span className="block text-sm font-semibold tracking-tight text-navy">MediSource</span>
        <span className="block text-[11px] font-medium uppercase tracking-[0.16em] text-teal-dark">Ghana</span>
      </span>
    </Link>
  );
}
