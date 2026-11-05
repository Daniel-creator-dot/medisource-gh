# API specification

Base path `/api/v1`. Success responses use `{ "data": ..., "meta": {} }`. Errors use `{ "error": { "code", "message", "details" } }`.

| Method | Path | Access |
| --- | --- | --- |
| GET | `/health/` | Public |
| GET | `/auth/csrf/` | Public |
| POST | `/auth/login/` | Public, CSRF for cookie clients |
| POST | `/auth/mfa/verify/` | Public |
| POST | `/auth/mfa/enroll/` | Signed in |
| POST | `/auth/mfa/confirm/` | Signed in |
| GET | `/auth/me/` | Signed in |
| POST | `/auth/logout/` | Signed in |
| GET | `/auth/users/` | Agency owner |
| GET | `/agency/` | Agency roles |
| GET | `/clients/` | Agency roles and the signed-in client |
| GET | `/clients/{slug}/` | Same scope; other clients return 404 |
| GET | `/command-center/` | Agency roles and the signed-in client |
| GET | `/employees/` | Agency, the client's deployed workers, or the employee |
| GET | `/me/employment/` | The linked employee |
| POST | `/attendance-events/{id}/adjustments/` | Agency roles |

OpenAPI is served at `/api/schema/` and `/api/docs/`.

Command-center finance fields are null. `finance.reason` explains that payroll and billing are not active.
