import { apiRequest } from "@medisource/api-client";
import type {
  Category,
  Envelope,
  ProductCard,
  ProductDetail,
  SupplierCard,
  SupplierDetail,
} from "@medisource/shared-types";

export function getCategories() {
  return apiRequest<Envelope<Category[]>>("/api/v1/catalog/categories/");
}

export function getProducts(search: Record<string, string | undefined>) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(search)) {
    if (value) {
      params.set(key, value);
    }
  }
  const query = params.toString();
  return apiRequest<Envelope<ProductCard[]>>(`/api/v1/catalog/products/${query ? `?${query}` : ""}`);
}

export function getProduct(slug: string) {
  return apiRequest<Envelope<ProductDetail>>(`/api/v1/catalog/products/${slug}/`);
}

export function getSuppliers() {
  return apiRequest<Envelope<SupplierCard[]>>("/api/v1/catalog/suppliers/");
}

export function getSupplier(slug: string) {
  return apiRequest<Envelope<SupplierDetail>>(`/api/v1/catalog/suppliers/${slug}/`);
}
