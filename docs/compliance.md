# Compliance boundaries

This note is product and engineering guidance. It is not legal advice and it is not evidence that MediSource GH is licensed, certified, or registered.

## Do not imply approval that does not exist

- Sample suppliers, products, and accounts are fictional. The interface says so.
- `verification_status = demo` is not a verification decision.
- No clinician, nurse, midwife, or pharmacist is listed, because a fictional licence would look like a real one.
- No customer rating, regulatory certificate, or FDA approval is seeded.
- The category policy text describes a development rule. It is not an authorization from the Food and Drugs Authority, the Pharmacy Council, HeFRA, or a professional council.

## Commercial and clinical limits in this build

- Authorized pharmaceutical products can exist as a category, and checkout for that category is off.
- No prescription capture, dispensing, or medicine recommendation flow is implemented.
- Appointment booking is not implemented. The public page describes the future control: expired or suspended credentials block the related services, and verification is a human decision.
- Home-care services are not offered.
- AI is not connected and will not be allowed to diagnose, prescribe, or approve a professional.

## Ghana frameworks to clear before production processing

Counsel and the relevant regulators need to confirm which of these apply to the live service. The engineering work should assume they matter:

- Data Protection Act, 2012 (Act 843), including a lawful basis, purpose limitation, security, and registration if the Data Protection Commission requires it for this processing.
- Food and Drugs Authority requirements for medical devices, diagnostics, and medicines that the marketplace actually sells.
- Pharmacy Council rules before any pharmacy or medicine activity.
- Health Facilities Regulatory Agency requirements for facility services.
- Professional council rules (Medical and Dental Council, Nursing and Midwifery Council, Allied Health Professions Council, and others that match the role) before a person is shown as bookable.
- Tax, electronic money, and payment-service rules before Mobile Money, cards, or credit terms go live.

## Data collected now

- Account name, email, optional phone, password hash, and addresses the customer saves.
- Authentication audit events and MFA secrets in encrypted form.
- Contact inquiries submitted through the form.
- Demo catalogue content.

The privacy page on the site matches this list. Marketing consent is not collected because there is no mailing list.

## Payments

Sandbox and live gateway credentials are not configured. The ledger and webhook verifier are future work. Until they exist, the product must not show an order as paid.

## Launch gates

Production launch of a new domain waits until:

1. The legal basis for that data and activity is confirmed.
2. The category policy for anything sold is an explicit decision, not a seed default.
3. Privileged MFA is on.
4. Backups, HTTPS, secret storage, and audit review are operating.
5. The automated tests for that domain, including the abuse cases in the implementation plan, are passing.
