# Database model

PostgreSQL is the system of record. The diagram below is the schema created by the current migrations. Later domains are listed after the diagram and do not have tables yet.

```mermaid
erDiagram
    User ||--o{ Membership : has
    User ||--o{ Address : keeps
    User ||--o{ OneTimeToken : receives
    User ||--o{ MfaFactor : enrolls
    User ||--o{ Notification : receives
    User ||--o{ AuditLog : acts
    Organization ||--o{ Membership : grants
    Organization ||--o| Supplier : profiles
    Organization ||--o{ AuditLog : scopes
    Category ||--|| CategoryPolicy : governs
    Category ||--o{ MasterProduct : classifies
    MasterProduct ||--o{ Listing : offered_as
    Supplier ||--o{ Listing : sells

    User {
        uuid id
        string email
        string platform_role
        bool email_verified
        bool mfa_enabled
        bool is_demo_account
    }
    Organization {
        uuid id
        string slug
        string org_type
        string status
    }
    Membership {
        uuid id
        string role
        bool is_active
    }
    Address {
        uuid id
        string region
        string country
        bool is_default
    }
    MfaFactor {
        uuid id
        string method
        string secret_encrypted
        datetime confirmed_at
    }
    CategoryPolicy {
        uuid id
        bool checkout_enabled
        bool requires_authorization
        string policy_reference
    }
    MasterProduct {
        uuid id
        string slug
        string manufacturer
        string pack_size
        bool is_demo
    }
    Supplier {
        uuid id
        string slug
        string verification_status
        bool is_demo
        string internal_notes
    }
    Listing {
        uuid id
        decimal price_amount
        int stock_quantity
        int minimum_order_quantity
        string status
        bool is_demo
    }
    AuditLog {
        uuid id
        string action
        string resource_type
        json metadata
    }
    Notification {
        uuid id
        string title
        bool is_read
    }
    ContactInquiry {
        uuid id
        string topic
        string message
    }
```

## Constraints that protect invariants

- One membership row per user and organization.
- One default address per user.
- One active TOTP factor per user.
- Listing price and stock cannot be negative.
- Minimum order quantity is at least 1.
- Supplier SKU is unique per supplier.
- Email is stored lowercase and is unique.

## Planned tables (not migrated)

These names describe the next slices. Columns will be designed in the migration that introduces them.

- Credential document, review decision, and expiry for professionals and suppliers.
- Cart, customer order, merchant order, and order event.
- Payment intent, ledger entry, webhook receipt, and settlement.
- Warehouse, stock lot, reservation, shipment, and proof of delivery.
- Professional service, availability rule, slot hold, and appointment.
- Requisition, approval step, RFQ, quotation, purchase order, and goods receipt.

Appointment overlap will use a PostgreSQL exclusion constraint on the resource and the active time range. Payment webhook receipts will be unique on provider plus event id.
