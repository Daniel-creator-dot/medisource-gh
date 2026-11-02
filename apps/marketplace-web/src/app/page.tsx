import { Button } from "@medisource/ui";
import { MediSourceApiError } from "@medisource/api-client";
import type { Category, ProductCard, SupplierCard } from "@medisource/shared-types";
import { Building2, ShieldCheck, Stethoscope, Truck } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { CategoryCard } from "@/components/category-card";
import { ProductCard as ProductCardView } from "@/components/product-card";
import { SearchForm } from "@/components/search-form";
import { ErrorState } from "@/components/states";
import { SupplierCard as SupplierCardView } from "@/components/supplier-card";
import { getCategories, getProducts, getSuppliers } from "@/lib/catalog";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const catalog = await loadCatalog();
  return (
    <>
      <section className="bg-navy text-white">
        <div className="mx-auto grid max-w-6xl gap-12 px-4 py-16 lg:grid-cols-[1.2fr_0.8fr] lg:py-24">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-care">Healthcare marketplace</p>
            <h1 className="mt-4 max-w-xl text-4xl font-semibold tracking-tight sm:text-5xl">
              Eligible supplies, verified suppliers, and a path to credentialed care.
            </h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-white/80">
              MediSource GH connects customers, suppliers, and facilities around products that a category policy
              allows. Sample rows in this environment are labelled and cannot be bought.
            </p>
            <div className="mt-8 max-w-xl">
              <SearchForm tone="dark" />
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button asChild variant="primary" size="lg">
                <Link href="/shop">Browse the shop</Link>
              </Button>
              <Button asChild variant="secondary" size="lg">
                <Link href="/suppliers">View suppliers</Link>
              </Button>
            </div>
          </div>
          <aside className="rounded-3xl border border-white/10 bg-white/5 p-6">
            <p className="text-sm font-semibold text-care">Live catalogue counts</p>
            <dl className="mt-6 grid grid-cols-3 gap-4">
              <Stat label="Categories" value={catalog.categories.length} />
              <Stat label="Products" value={catalog.products.length} />
              <Stat label="Suppliers" value={catalog.suppliers.length} />
            </dl>
            <p className="mt-6 text-sm leading-6 text-white/70">
              These counts come from the API. They are not marketing metrics, ratings, or proof of regulatory approval.
            </p>
          </aside>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <SectionHeading
          eyebrow="Categories"
          title="Browse by healthcare category"
          body="Checkout follows the category policy stored in the database. Pharmaceuticals stay closed in this release."
        />
        {catalog.error ? <ErrorState title="Catalogue unavailable" body={catalog.error} /> : null}
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {catalog.categories.slice(0, 6).map((category) => (
            <CategoryCard key={category.id} category={category} />
          ))}
        </div>
        <Link href="/categories" className="mt-6 inline-block text-sm font-semibold text-teal-dark">
          All categories
        </Link>
      </section>

      <section className="bg-white">
        <div className="mx-auto max-w-6xl px-4 py-16">
          <SectionHeading
            eyebrow="Products"
            title="Featured sample products"
            body="Every card is a master product with one or more supplier listings. Specifications are not copied onto each supplier."
          />
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {catalog.products.slice(0, 4).map((product) => (
              <ProductCardView key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <SectionHeading
          eyebrow="Suppliers"
          title="Sample supplier storefronts"
          body="A demo status is not a verification decision. Pending suppliers stay out of this directory."
        />
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {catalog.suppliers.map((supplier) => (
            <SupplierCardView key={supplier.id} supplier={supplier} />
          ))}
        </div>
      </section>

      <section className="bg-white">
        <div className="mx-auto grid max-w-6xl gap-6 px-4 py-16 lg:grid-cols-2">
          <InfoPanel
            icon={<Stethoscope className="h-5 w-5" />}
            title="Find a healthcare professional"
            body="Profiles appear only after a person reviews a current credential. The directory lists professions and regions now. It does not list sample clinicians, licences, or ratings."
            href="/professionals"
            action="Open the directory"
          />
          <InfoPanel
            icon={<Building2 className="h-5 w-5" />}
            title="Book an appointment"
            body="Booking is not open yet. When it is, a database constraint will stop two people from holding the same clinician slot. Payment status and cancellation rules will be part of that transaction."
            href="/appointments"
            action="See the booking rules"
          />
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <SectionHeading eyebrow="How it works" title="Designed as one controlled marketplace" body="" />
        <ol className="mt-8 grid gap-4 md:grid-cols-4">
          {[
            ["Live", "Browse eligible supplies from the public catalogue."],
            ["Next", "A reviewer verifies a supplier. Upload alone does not approve them."],
            ["Live", "Save a listing in your cart. Checkout stays closed for sample rows and pharmaceuticals."],
            ["Next", "A verified professional offers only the services their credential allows."],
          ].map(([state, text], index) => (
            <li key={text} className="rounded-2xl border border-line bg-white p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal-dark">
                {index + 1}. {state}
              </p>
              <p className="mt-3 text-sm leading-6 text-ink">{text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="bg-white">
        <div className="mx-auto grid max-w-6xl gap-4 px-4 py-16 md:grid-cols-3">
          <Benefit
            icon={<Building2 className="h-5 w-5" />}
            title="For hospitals"
            body="Procurement, approvals, and goods receipt are the next facility slice. Budgets and roles will live on the server, not only in the interface."
          />
          <Benefit
            icon={<Truck className="h-5 w-5" />}
            title="For suppliers"
            body="Listings attach to a master product. Price, stock, lead time, and delivery zones stay with the supplier. Private notes are not on the public storefront."
          />
          <Benefit
            icon={<ShieldCheck className="h-5 w-5" />}
            title="For healthcare workers"
            body="A profile becomes bookable only after review. Suspension or expiry removes the affected services. MediSource does not invent licences or reviews."
          />
        </div>
      </section>

      <section className="bg-navy text-white">
        <div className="mx-auto max-w-6xl px-4 py-16">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-care">Trust and compliance</p>
          <h2 className="mt-3 text-3xl font-semibold">Built for review, not for implied approval</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {[
              "Category policy can close checkout without deleting the product. Authorized pharmaceuticals are closed.",
              "Account data, addresses, and contact messages are the personal data collected in this release. Clinical records are not.",
              "Production use still needs the relevant Ghana regulatory and data-protection decisions. This site does not claim them.",
            ].map((item) => (
              <p key={item} className="rounded-2xl border border-white/10 p-5 text-sm leading-6 text-white/80">
                {item}
              </p>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}

async function loadCatalog(): Promise<{
  categories: Category[];
  products: ProductCard[];
  suppliers: SupplierCard[];
  error: string | null;
}> {
  try {
    const [categories, products, suppliers] = await Promise.all([getCategories(), getProducts({}), getSuppliers()]);
    return {
      categories: categories.data,
      products: products.data,
      suppliers: suppliers.data,
      error: null,
    };
  } catch (error) {
    const message =
      error instanceof MediSourceApiError
        ? error.message
        : "The catalogue service is not reachable.";
    const hint =
      process.env.NEXT_PUBLIC_ENVIRONMENT === "render"
        ? " On the free Render host the API sleeps after about 15 minutes. Wait a minute and refresh."
        : "";
    return { categories: [], products: [], suppliers: [], error: `${message}${hint}` };
  }
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-[0.12em] text-white/60">{label}</dt>
      <dd className="mt-1 text-3xl font-semibold">{value}</dd>
    </div>
  );
}

function SectionHeading({ eyebrow, title, body }: { eyebrow: string; title: string; body: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal-dark">{eyebrow}</p>
      <h2 className="mt-2 text-3xl font-semibold tracking-tight text-navy">{title}</h2>
      {body ? <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">{body}</p> : null}
    </div>
  );
}

function InfoPanel({
  icon,
  title,
  body,
  href,
  action,
}: {
  icon: ReactNode;
  title: string;
  body: string;
  href: string;
  action: string;
}) {
  return (
    <article className="rounded-3xl border border-line p-6">
      <div className="grid h-10 w-10 place-items-center rounded-xl bg-canvas text-teal-dark">{icon}</div>
      <h2 className="mt-4 text-2xl font-semibold text-navy">{title}</h2>
      <p className="mt-3 text-sm leading-6 text-muted">{body}</p>
      <Link href={href} className="mt-5 inline-block text-sm font-semibold text-teal-dark">
        {action}
      </Link>
    </article>
  );
}

function Benefit({ icon, title, body }: { icon: ReactNode; title: string; body: string }) {
  return (
    <article className="rounded-2xl border border-line p-5">
      <div className="text-teal-dark">{icon}</div>
      <h3 className="mt-3 text-lg font-semibold text-navy">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-muted">{body}</p>
    </article>
  );
}
