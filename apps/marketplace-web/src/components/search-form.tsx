export function SearchForm({
  initialQuery = "",
  action = "/shop",
  tone = "light",
}: {
  initialQuery?: string;
  action?: string;
  tone?: "light" | "dark";
}) {
  const light = tone === "light";
  return (
    <form action={action} className="flex w-full gap-2" role="search">
      <label className="sr-only" htmlFor="catalogue-search">
        Search products and suppliers
      </label>
      <input
        id="catalogue-search"
        name="q"
        defaultValue={initialQuery}
        placeholder="Search gloves, diagnostics, furniture..."
        className={
          light
            ? "h-12 flex-1 rounded-full border border-line bg-white px-5 text-sm text-ink outline-none focus-visible:ring-2 focus-visible:ring-teal"
            : "h-12 flex-1 rounded-full border border-white/15 bg-white px-5 text-sm text-ink outline-none"
        }
      />
      <button
        type="submit"
        className="h-12 rounded-full bg-teal-dark px-5 text-sm font-semibold text-white hover:bg-teal"
      >
        Search
      </button>
    </form>
  );
}
