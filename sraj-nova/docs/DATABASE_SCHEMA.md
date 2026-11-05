# Database schema

Primary keys are UUIDs. The implemented tables are:

- `organization_agency`, `organization_client`, `organization_clientsite`, `organization_department`, `organization_jobposition`, `organization_servicecontract`
- `workforce_employee`, `workforce_employeeidentifier`, `workforce_employmentcontract`, `workforce_deployment`
- `operations_shiftassignment`, `operations_attendanceevent`, `operations_attendanceadjustment`, `operations_staffingrequest`, `operations_operationalalert`
- `identity_user`
- `governance_auditevent`, `governance_outboxmessage`

`workforce_employmentcontract` requires a client when `legal_employer_kind` is `client`, and forbids a client when the kind is `agency`.

`workforce_employeeidentifier.ciphertext` stores a Fernet value derived from the Django secret. Seeded values use the prefix `SAMPLE-NOT-A-REAL-ID` and are not returned by the employee API.

Payroll, payment, invoice, and ledger tables are not created yet.
