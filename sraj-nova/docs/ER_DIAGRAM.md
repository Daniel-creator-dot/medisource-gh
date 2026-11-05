# Entity relationships

```mermaid
erDiagram
  Agency ||--o{ Client : serves
  Client ||--o{ ClientSite : has
  ClientSite ||--o{ Department : has
  Client ||--o{ JobPosition : defines
  Client ||--o{ ServiceContract : signs
  Employee ||--o{ EmploymentContract : holds
  Client ||--o{ EmploymentContract : may_employ
  Employee ||--o{ Deployment : assigned
  Client ||--o{ Deployment : receives
  Client ||--o{ ShiftAssignment : schedules
  Employee ||--o{ AttendanceEvent : records
  AttendanceEvent ||--o{ AttendanceAdjustment : corrects
  User }o--|| Client : scoped_to
  User }o--|| Employee : scoped_to
```

A user is an agency role, a single client user, or a single employee. The legal employer on the employment contract is independent of which organization currently hosts the deployment.
