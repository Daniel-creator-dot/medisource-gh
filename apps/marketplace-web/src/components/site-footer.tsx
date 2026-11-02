import Link from "next/link";

const columns = [
  {
    title: "Marketplace",
    links: [
      ["/shop", "Shop products"],
      ["/cart", "Cart"],
      ["/suppliers", "Suppliers"],
      ["/categories", "Categories"],
      ["/professionals", "Professionals"],
    ],
  },
  {
    title: "Company",
    links: [
      ["/about", "About"],
      ["/services", "Services"],
      ["/facilities", "Facilities"],
      ["/contact", "Contact"],
    ],
  },
  {
    title: "Help",
    links: [
      ["/help", "Help centre"],
      ["/appointments", "Appointments"],
      ["/privacy", "Privacy"],
      ["/terms", "Terms"],
    ],
  },
] as const;

export function SiteFooter() {
  return (
    <footer className="bg-navy text-white">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-14 md:grid-cols-4">
        <div>
          <p className="text-lg font-semibold">MediSource GH</p>
          <p className="mt-3 text-sm leading-6 text-white/75">
            A healthcare marketplace for eligible supplies, verified suppliers, and, in later releases, credentialed
            professionals.
          </p>
        </div>
        {columns.map((column) => (
          <div key={column.title}>
            <p className="text-sm font-semibold">{column.title}</p>
            <ul className="mt-3 space-y-2 text-sm text-white/75">
              {column.links.map(([href, label]) => (
                <li key={href}>
                  <Link href={href} className="hover:text-white">
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-white/10">
        <p className="mx-auto max-w-6xl px-4 py-4 text-xs text-white/60">
          Sample catalogue data is fictional. MediSource GH does not claim regulatory approval, professional
          registration, or payment-provider certification in this development release.
        </p>
      </div>
    </footer>
  );
}
