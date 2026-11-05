# Test strategy

Backend tests live in `modules/organization/tests/test_access.py` and use SQLite in memory.

They check:

- A client user cannot see the other sample client's workers, client page, or command-center row, and cannot list accounts.
- Finance totals are null.
- An employee cannot open the command center or client list and can open only their own record.
- Identification sample values are absent from the employee response.
- Command-center counts match the seeded shifts: 4 active, 4 scheduled, 1 unfilled, 2 on duty, 1 late, 1 absent, 1 pending request, 1 expiring contract.
- One current contract names the client as legal employer.
- An attendance adjustment does not change the original timestamp.
- With MFA required, an owner without an authenticator gets no session.
- Health reports the database check, and the owner can list four demonstration accounts.

Frontend typecheck and lint are run with `npm run typecheck` and `npm run lint`. Browser checks cover sign-in and the command center against the running API.

Payroll calculation tests will be added only with the payroll milestone.
