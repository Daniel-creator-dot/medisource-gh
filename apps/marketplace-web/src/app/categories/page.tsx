import type { Metadata } from "next";

import { CategoryCard } from "@/components/category-card";
import { PageHeader } from "@/components/page-header";
import { ErrorState } from "@/components/states";
import { getCategories } from "@/lib/catalog";
import { MediSourceApiError } from "@medisource/api-client";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Categories" };

export default async function CategoriesPage() {
  let categories: Awaited<ReturnType<typeof getCategories>>["data"] | null = null;
  let errorMessage: string | null = null;
  try {
    categories = (await getCategories()).data;
  } catch (error) {
    errorMessage = error instanceof MediSourceApiError ? error.message : "Categories could not be loaded.";
  }
  if (errorMessage || !categories) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <ErrorState title="Categories unavailable" body={errorMessage ?? "Categories could not be loaded."} />
      </div>
    );
  }
  return (
    <>
      <PageHeader
        eyebrow="Categories"
        title="Product categories"
        body="An open policy means a verified, non-sample listing in that category can later be checked out. A closed policy blocks checkout even if a product is visible."
      />
      <div className="mx-auto grid max-w-6xl gap-4 px-4 py-10 md:grid-cols-2">
        {categories.map((category) => (
          <CategoryCard key={category.id} category={category} />
        ))}
      </div>
    </>
  );
}
