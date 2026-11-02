import type { Metadata } from "next";

import { PageHeader } from "@/components/page-header";
import { ProductCard } from "@/components/product-card";
import { EmptyState, ErrorState } from "@/components/states";
import { getCategories, getProducts, getSuppliers } from "@/lib/catalog";
import { firstParam } from "@/lib/format";
import { MediSourceApiError } from "@medisource/api-client";
import Link from "next/link";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Shop" };

export default async function ShopPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const q = firstParam(params.q) ?? "";
  const category = firstParam(params.category) ?? "";
  const supplier = firstParam(params.supplier) ?? "";
  const ordering = firstParam(params.ordering) ?? "name";
  const page = firstParam(params.page) ?? "1";

  let products: Awaited<ReturnType<typeof getProducts>> | null = null;
  let categories: Awaited<ReturnType<typeof getCategories>> | null = null;
  let suppliers: Awaited<ReturnType<typeof getSuppliers>>["data"] | null = null;
  let errorMessage: string | null = null;
  try {
    const [productPage, categoryPage, supplierPage] = await Promise.all([
      getProducts({ q, category, supplier, ordering, page }),
      getCategories(),
      getSuppliers({}),
    ]);
    products = productPage;
    categories = categoryPage;
    suppliers = supplierPage.data;
  } catch (error) {
    errorMessage = error instanceof MediSourceApiError ? error.message : "The catalogue could not be loaded.";
  }
  if (errorMessage || !products || !categories || !suppliers) {
    return (
      <>
        <PageHeader eyebrow="Shop" title="Healthcare products" body="The catalogue is loaded from the API." />
        <div className="mx-auto max-w-6xl px-4 py-10">
          <ErrorState title="Catalogue unavailable" body={errorMessage ?? "The catalogue could not be loaded."} />
        </div>
      </>
    );
  }
  const meta = products.meta as { page?: number; pages?: number };
  return (
      <>
        <PageHeader
          eyebrow="Shop"
          title="Healthcare products"
          body="Prices and stock come from supplier listings. Sample rows stay visible for development and cannot be purchased."
        />
        <div className="mx-auto max-w-6xl px-4 py-10">
          <form action="/shop" className="grid gap-3 rounded-2xl border border-line bg-white p-4 md:grid-cols-2 xl:grid-cols-[1fr_200px_200px_180px_auto]">
            <input
              name="q"
              defaultValue={q}
              placeholder="Search products"
              aria-label="Search products"
              className="h-12 rounded-full border border-line px-5 text-sm outline-none focus-visible:ring-2 focus-visible:ring-teal md:col-span-2 xl:col-span-1"
            />
            <label className="sr-only" htmlFor="category">
              Category
            </label>
            <select
              id="category"
              name="category"
              defaultValue={category}
              className="h-12 rounded-full border border-line bg-white px-4 text-sm"
            >
              <option value="">All categories</option>
              {categories.data.map((item) => (
                <option key={item.id} value={item.slug}>
                  {item.name}
                </option>
              ))}
            </select>
            <label className="sr-only" htmlFor="supplier">
              Supplier
            </label>
            <select
              id="supplier"
              name="supplier"
              defaultValue={supplier}
              className="h-12 rounded-full border border-line bg-white px-4 text-sm"
            >
              <option value="">All suppliers</option>
              {suppliers.map((item) => (
                <option key={item.id} value={item.slug}>
                  {item.display_name}
                </option>
              ))}
            </select>
            <label className="sr-only" htmlFor="ordering">
              Sort
            </label>
            <select
              id="ordering"
              name="ordering"
              defaultValue={ordering}
              className="h-12 rounded-full border border-line bg-white px-4 text-sm"
            >
              <option value="name">Name</option>
              <option value="price">Price, low to high</option>
              <option value="-price">Price, high to low</option>
            </select>
            <button type="submit" className="h-12 rounded-full bg-navy px-5 text-sm font-semibold text-white">
              Apply
            </button>
          </form>
          <p className="mt-4 text-sm text-muted">
            {"count" in products.meta
              ? `${products.meta.count} product${products.meta.count === 1 ? "" : "s"}`
              : null}
            {q || category || supplier ? (
              <>
                {" "}
                <Link href="/shop" className="font-semibold text-teal-dark">
                  Clear filters
                </Link>
              </>
            ) : null}
          </p>
          {products.data.length === 0 ? (
            <div className="mt-8">
              <EmptyState title="No products match" body="Try another search or clear the category filter." />
            </div>
          ) : (
            <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {products.data.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
          {meta.pages && meta.pages > 1 ? (
            <nav className="mt-8 flex gap-3 text-sm" aria-label="Pagination">
              {Array.from({ length: meta.pages }, (_, index) => {
                const number = String(index + 1);
                const query = new URLSearchParams({ q, category, supplier, ordering, page: number });
                return (
                  <Link
                    key={number}
                    href={`/shop?${query.toString()}`}
                    className={`rounded-full px-3 py-1 ${number === String(meta.page) ? "bg-navy text-white" : "bg-white text-navy"}`}
                  >
                    {number}
                  </Link>
                );
              })}
            </nav>
          ) : null}
        </div>
      </>
  );
}
