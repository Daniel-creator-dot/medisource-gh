export type PageMeta = {
  count: number;
  page: number;
  page_size: number;
  pages: number;
};

export type Envelope<T> = {
  data: T;
  meta: PageMeta | Record<string, never>;
};

export type ApiErrorBody = {
  error: {
    code: string;
    message: string;
    details: unknown;
  };
};

export type User = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  platform_role: string;
  email_verified: boolean;
  mfa_enabled: boolean;
  is_demo_account: boolean;
};

export type SessionPayload = {
  user: User | null;
  mfa_required: boolean;
  enrollment_required: boolean;
  access: string | null;
  refresh: string | null;
  mfa_token: string | null;
};

export type Address = {
  id: string;
  label: string;
  recipient_name: string;
  phone_number: string;
  line1: string;
  line2: string;
  city: string;
  region: string;
  postal_code: string;
  country: string;
  is_default: boolean;
};

export type NotificationItem = {
  id: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
};

export type Membership = {
  id: string;
  role: string;
  is_active: boolean;
  organization: {
    id: string;
    name: string;
    slug: string;
    org_type: string;
    status: string;
  };
};

export type Category = {
  id: string;
  name: string;
  slug: string;
  description: string;
  checkout_enabled: boolean;
  requires_authorization: boolean;
  policy_reference: string;
  product_count: number;
};

export type Money = {
  amount: string;
  currency: string;
};

export type SupplierCard = {
  id: string;
  display_name: string;
  slug: string;
  summary: string;
  city: string;
  region: string;
  verification_status: string;
  is_demo: boolean;
  demo_label: string | null;
  active_listing_count: number | null;
};

export type ProductCard = {
  id: string;
  name: string;
  slug: string;
  brand: string;
  manufacturer: string;
  pack_size: string;
  unit_of_measure: string;
  is_demo: boolean;
  demo_label: string | null;
  category_name: string;
  category_slug: string;
  lowest_price: Money | null;
  supplier_count: number;
  can_purchase: boolean;
  purchase_block_reason: string | null;
};

export type Listing = {
  id: string;
  sku: string;
  price_amount: string;
  currency: string;
  stock_quantity: number;
  minimum_order_quantity: number;
  lead_time_days: number;
  warehouse_name: string;
  delivery_zones: string[];
  status: string;
  is_demo: boolean;
  supplier: SupplierCard;
  can_purchase: boolean;
  purchase_block_reason: string | null;
};

export type ProductDetail = ProductCard & {
  generic_name: string;
  description: string;
  specification: string;
  strength: string;
  dosage_form: string;
  gtin: string;
  regulatory_notes: string;
  listings: Listing[];
};

export type SupplierListing = {
  id: string;
  sku: string;
  price_amount: string;
  currency: string;
  stock_quantity: number;
  minimum_order_quantity: number;
  lead_time_days: number;
  warehouse_name: string;
  delivery_zones: string[];
  is_demo: boolean;
  product_name: string;
  product_slug: string;
  can_purchase: boolean;
  purchase_block_reason: string | null;
};

export type SupplierDetail = SupplierCard & {
  listings: SupplierListing[];
};
