"use client";

import { Menu, X } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

const links = [
  ["/shop", "Shop"],
  ["/categories", "Categories"],
  ["/suppliers", "Suppliers"],
  ["/professionals", "Professionals"],
  ["/about", "About"],
  ["/contact", "Contact"],
] as const;

export function MobileNav() {
  const [open, setOpen] = useState(false);
  return (
    <div className="md:hidden">
      <button
        type="button"
        className="grid h-10 w-10 place-items-center rounded-full border border-line"
        aria-expanded={open}
        aria-controls="mobile-menu"
        onClick={() => setOpen((value) => !value)}
      >
        {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        <span className="sr-only">Menu</span>
      </button>
      {open ? (
        <div id="mobile-menu" className="absolute inset-x-0 top-full border-b border-line bg-white px-4 py-3 shadow-sm">
          <nav className="grid gap-1" aria-label="Mobile">
            {links.map(([href, label]) => (
              <Link
                key={href}
                href={href}
                className="rounded-xl px-3 py-2 text-sm font-medium text-navy hover:bg-canvas"
                onClick={() => setOpen(false)}
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
      ) : null}
    </div>
  );
}
