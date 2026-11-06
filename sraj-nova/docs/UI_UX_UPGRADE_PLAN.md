# UI and UX upgrade plan

Inspection date: 6 November 2026. The interface lives in `sraj-nova/apps/command-web` (Next.js App Router, Tailwind 4, no chart or motion library).

## What is already on screen

Signed-in routes that load stored records: Command, Actions, Floor, Coverage, People, Finance, Books, Clients, Agency, Access, My record. Actions write a shift, an attendance event, or a staffing request. Coverage assigns a recommended worker. Finance rebuilds the current week’s invoices. Books post the week and record a receipt. Theme switching stores `nova-theme` on the document.

The previous visual system was warm paper, copper, and a dark brown rail. It is readable. It does not yet look like a financial control surface, and several requested charts have no stored series behind them.

## Phase 1, this delivery

- One token set: midnight navy `#071426`, electric blue `#2f6bff`, SRAJ orange `#e36a1e`, paper white and grey in light mode, the same tokens inverted for dark mode.
- Existing classes (`.panel`, `.metric`, `.gauge`, `.sheet`, `.rail`) pick up the tokens, so every current page changes without new routes.
- Glass panels are a light backdrop blur. `prefers-reduced-transparency` falls back to a solid card. `prefers-reduced-motion` turns off transitions.
- The command center is reorganised into workforce counts, money that is actually stored, today’s attendance mix, deployment by client, and a lower band of alerts, exceptions, certifications, and unpaid invoices.
- Missing figures stay labelled “Not calculated” or “Not scheduled”. They are not drawn as zero.

Motion for React, Apache ECharts, and React Flow are not added in this phase. The only workforce series in the database is the current week of shifts and the current client invoices. A trend line or an approval diagram would have to invent points. Those libraries belong in Phase 6, after payroll runs, invoice history, and an approval table exist. Optional 3D is out of scope for the same reason.

## Later visual work

- Page transition only if it stays under one frame and respects reduced motion.
- ECharts for payroll, cash, and attendance once those series are queried from stored weeks.
- React Flow only for a workflow that has real states in the database.
- Table expansion on the books screen after journal lines are already listed, which they are.
- Skeleton states on the existing `apiGet` wait. Do not animate accounting entry forms.
