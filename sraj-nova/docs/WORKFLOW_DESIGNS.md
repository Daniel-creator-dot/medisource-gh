# Workflow designs

## Sign-in

The browser requests a CSRF token, then posts email and password. A successful response sets `nova_access` and `nova_refresh`. When production MFA is required and the owner is not enrolled, the API returns 403 and does not set cookies.

## Attendance correction

A supervisor posts a reason. The API inserts `AttendanceAdjustment` and leaves `AttendanceEvent.occurred_at` unchanged. This is covered by a test.

## Command center

The API counts active employees, current deployments, today's assigned and unfilled shifts, and classifies each assigned shift from attendance events: no `in` event is absent, an `in` after start plus `LATE_GRACE_MINUTES` is late, and a last event of `in` is on duty. The grace value is 10 minutes and is an operational setting, not a legal ruling.

## Not built

Offer approval, payroll approval, payment maker-checker, invoice approval, and period close are later milestones. There are no buttons for them.
