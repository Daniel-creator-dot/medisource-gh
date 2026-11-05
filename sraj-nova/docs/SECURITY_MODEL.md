# Security model

- Roles gate each API. Client and employee queries are filtered before serialization. A missing client returns 404 rather than another client's record.
- Access tokens are HttpOnly cookies. Cookie mutations require CSRF unless the caller sends a bearer token or `X-Client: mobile`.
- Local cookies are SameSite Lax. Production settings use Secure cookies and SameSite None.
- Agency-owner authenticator enrollment is required by production settings and tested. The demonstration seed does not enroll an authenticator.
- Identifier values are encrypted at rest and are not returned by the current APIs.
- Audit and outbox rows are written together for sign-in. The outbox is not published.
- The seed command refuses to run when `DEBUG` is false unless `FORCE_SEED_DEMO` is set.
- Rate limiting, document storage, backup jobs, and a security monitoring sink are not implemented yet.
- This milestone does not claim compliance with Ghana data-protection, tax, or pension rules.
