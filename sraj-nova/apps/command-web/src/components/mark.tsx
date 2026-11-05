export function Mark({ light = false }: { light?: boolean }) {
  const steel = light ? "#ffffff" : "var(--ink)";
  return (
    <span className="inline-flex items-center gap-2">
      <svg aria-hidden="true" width="28" height="28" viewBox="0 0 28 28">
        <rect width="28" height="28" rx="7" fill="#e36a1e" />
        <path d="M8 21V7h3.1l3.4 6.2V7h3.1v14h-3.1l-3.4-6.2V21H8Z" fill="#0b1f33" />
      </svg>
      <span className="display text-lg font-semibold" style={{ color: steel }}>
        SRAJ NOVA
      </span>
    </span>
  );
}
