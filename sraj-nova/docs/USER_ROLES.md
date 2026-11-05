# User roles

| Role | Sees |
| --- | --- |
| `agency_owner` | All clients, workers, the agency record, and the account list |
| `agency_operations` | All clients and workers. Cannot list accounts |
| `agency_finance` | Same operational scope as operations. No payroll actions exist yet |
| `client_user` | One client, that client's sites, and workers currently deployed there |
| `employee` | Their own employment record. Command center and client lists return 403 |

A client user does not receive another client's workers or the legal-employer field on the worker list. Identification ciphertext is not included in any of these responses.

Production settings set `MFA_REQUIRED_FOR_AGENCY_OWNER`. An owner who has not enrolled an authenticator receives `mfa_enrollment_required` and no session cookie. The local demonstration leaves that requirement off so the command center can be reviewed.
