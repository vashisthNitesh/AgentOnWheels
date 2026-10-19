# What AgentOnWheels fixes compared with ATS Shipping

| ATS problem | AgentOnWheels |
|---|---|
| Login returned 200 but stayed on /login; 401 loops; tab hangs | JWT login only counts as successful after `/auth/me` loads. Silent refresh-token rotation, one shared refresh request, a clean redirect to `/login?next=`, clear error messages (wrong password / throttled / network), and login throttling (10/min) |
| "Open full order" did nothing | A dedicated `/orders/:id` page: status timeline, allowed next-step buttons, pickup/drop, cargo, legs & trips, invoices, audit, copy order no. |
| Completed order showing "0 of 1 committed / Allocation pending" | Committed vehicles and allocation are computed from the legs. Order status follows its legs; transitions are checked against a workflow (`Order.FLOW`). Confirming an order creates one leg per vehicle |
| Invoice due date 8 years out; invoicing company empty | Due date = invoice date + the customer's payment terms (not editable). Invoicing company defaults from the customer. Future invoice dates and paid-before-invoice are rejected |
| 18% GST on AED invoices | `TaxRule` per country + currency (UAE VAT 5%, KSA 15%, Oman 5%, India GST 18%), picked automatically from the branch country. Vendor invoices work the same way |
| Margin 100% because cost was always 0 | Legs carry buy rates (own fleet cost or vendor rate). The dashboard shows margin only when cost exists, plus "cost captured on X% of legs" |
| Drivers 8/14/34, maintenance 3 vs 4, idle 2 vs 5 | `services.fleet_snapshot()` is the one definition used by the dashboard and control tower. Vehicle status follows open maintenance. Attendance only counts real drivers |
| Fleet utilisation 1.1% looked wrong | Defined as own vehicle-days with a trip ÷ (own vehicles × days) and labelled that way |
| Bid past its window still Pending; lease past end "Created"; all contracts expired silently | `expire_statuses` (cron/loop, and run on dashboard load): bids become active → closed/expired, leases created → active → completed, contracts pending/active/expired from their dates, quotations and RFQs expire. Orders link to the active contract, and the order page warns when there isn't one. Dashboard shows contract coverage % |
| Driver passcodes in plain text, all 123456 | Hashed with Django's password hasher, write-only "Set passcode" action, weak codes (123456, repeated digits) rejected, list shows only Set / Not set |
| Indian cities with country UAE, AED on Indian lanes, UTC vs "Gulf time" | Location → Country (with currency, IANA timezone, phone code). Lane service type (domestic/cross-border) is derived from countries. Order currency comes from the branch country. All times stored in UTC and shown in one display timezone with a label |
| kg vs tonnes mismatch | Every weight is stored and shown in tonnes (`*_t` fields, "t" suffix, "(tonnes)" label) |
| Lists show "0 of 0" while loading, no spinner | Skeleton rows, request sequencing (no stale results), error banner with Retry, real empty states with a call to action |
| Wizard Next disabled with no explanation | Next is always clickable. It lists the missing required fields, highlights them, and server validation errors jump to the right step |
| Raw HTML `0" class="list-footer">` leaking | A single generic list component; no string-concatenated HTML |
| Duplicate rate inquiries; "rate not available" yet Approved | Duplicates (same customer/lane/product/date/commodity within 24h) rejected. Approval needs a sell price. No rate found → automatic sourcing request |
| "Monthly" lease of 9 days | Minimum length per lease type is checked |
| Vendor order requested 1 / remaining 1 / committed 1 | Remaining = requested − committed; committed can't exceed requested |
| Payout date before period end | Rejected |
| 5 duplicate open accident job cards; technician 5/4 over capacity | Duplicate open job card for the same vehicle and activity rejected; technician capacity enforced; workload shown |
| Trailers had no status | Status added (available / in use / maintenance / deactivated) |
| Rate master "customer rate" without a customer | Optional customer column (empty = standard tariff); customer-specific rate wins |
| On-the-road trips with "No ETA" labelled "On track"; month-old trips still on the road | Risk = late / no ETA / ETA past plan / on track; stale (>3 days) and GPS-silent flags; attention banner |
| Grammar ("All branch", "Ready For Invoice") | Consistent pluralised filter labels and sentence-case statuses |
| Reports with overlapping types and no parameters | Clear report types with date range + branch, downloadable as CSV |
| Mixed currencies in totals | Dashboard filters by branch (its currency); shows "MIXED" instead of adding up different currencies when branches use several |

## New KPIs
On-time delivery (more than 15 min late counts as late), real gross margin, cost coverage, fleet utilisation, unbilled value, overdue invoices, contract coverage, rate-inquiry hit rate, vendor bid response rate, % outsourced, confirmed-without-truck, orders stuck 48h+, lane punctuality, driver presence, and documents expiring or expired. Every KPI compares with the previous period of the same length, and all of them respond to the branch, customer, job type and date range filters.

## Not done yet (next steps)
Map view / GPS integration, driver mobile app, file attachments, role-based permissions beyond staff, email notifications, bulk allocate/reschedule UI, PDF invoices.
