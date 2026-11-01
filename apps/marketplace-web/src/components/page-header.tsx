export function PageHeader({ eyebrow, title, body }: { eyebrow?: string; title: string; body: string }) {
  return (
    <header className="border-b border-line bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12">
        {eyebrow ? (
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal-dark">{eyebrow}</p>
        ) : null}
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-navy sm:text-4xl">{title}</h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-muted">{body}</p>
      </div>
    </header>
  );
}
