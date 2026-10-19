# AgentOnWheels UI/UX Audit & Migration Baseline (Phase 0)

**Date:** 2026-10-20  
**Project:** AgentOnWheels Transport Management System (TMS)  
**Location:** `./frontend`  
**Author:** Senior Product Designer & Senior Vue 3 Frontend Engineer  

---

## 1. Stack Inventory

| Dimension | Current Implementation | Observations & Migration Notes |
|---|---|---|
| **Vue Version** | Vue 3.5.0 (`^3.5.0`) | SFC with `<script setup>`, Composition API. High compatibility with modern Vue 3 ecosystem. |
| **Router Version** | Vue Router 4.4.0 (`^4.4.0`) | HTML5 history mode (`createWebHistory()`), standard beforeEach auth guards. |
| **State Management** | Ad-hoc reactive object + Window global | `export const auth = reactive({ user: null, ready: false })` in `api.js` and `window.__refCache = {}` in `RefSelect.vue`. No global store library (Pinia) installed. Composables with `@vueuse/core` will provide clean localized state. |
| **Tailwind Version** | Tailwind CSS 3.4.0 (`^3.4.0`) | Configuration file-based (`tailwind.config.js`), PostCSS 8.4, Autoprefixer 10.4. Custom brand palette defined under `colors.brand`. |
| **Language** | JavaScript (ES Modules) | Standard `.js` and `.vue` files. No TypeScript configured; adhere to JS + JSDoc per Hard Constraint #5. |
| **UI Component Libraries** | None (100% custom raw HTML) | Native inputs, native `<select>`, rudimentary utility classes in `style.css` (`.btn`, `.input`, `.card`, `.th`, `.td`). |
| **Icon Set** | Unicode Emojis | Inline emojis ("🚚", "📈", "⚙️", "🏢", "📦") used for navigation, modules, and empty states. Lacks visual consistency, accessibility tags, and cross-platform fidelity. Will transition to `lucide-vue-next`. |
| **Chart Library** | Chart.js 4.4.0 + `vue-chartjs` 5.3.0 | Uses `Bar` and `Doughnut` charts in `Dashboard.vue`. Rigid sizing, hardcoded theme colors, lacks dark-mode reactiveness. Will transition to tree-shaken `echarts` + `vue-echarts`. |
| **HTTP Client** | Axios 1.7.0 (`^1.7.0`) | Configured instance in `src/api.js` with baseURL `/api/`, 30s timeout, Bearer token injection, and automatic 401 refresh token interceptor. Must be preserved untouched. |

---

## 2. Build Pipeline & Django Integration

### 2.1 Build Execution (`scripts/build.sh`)
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
(cd frontend && npm install && npm run build)
mkdir -p templates && cp frontend/dist/index.html templates/index.html
python manage.py collectstatic --noinput -v0
```

### 2.2 Vite Configuration (`frontend/vite.config.js`)
- **Base path:** `/static/` (Strict requirement for Django static asset serving).
- **Output directory:** `dist/` (cleaned with `emptyOutDir: true`).
- **Plugins:** `@vitejs/plugin-vue`.
- **Dev Server Proxy:** `/api` proxies to `http://127.0.0.1:8000`.

### 2.3 Django Template & Static Delivery
- **Static Assets:** `config/settings.py` declares `STATICFILES_DIRS = [BASE_DIR / "frontend" / "dist"]`, `STATIC_URL = "/static/"`, and `STATIC_ROOT = BASE_DIR / "staticfiles"`. WhiteNoise serves static bundles in production.
- **SPA Routing:** `config/urls.py` captures all non-API/non-static requests:
  ```python
  re_path(r"^(?!api/|static/|django-admin/).*$", TemplateView.as_view(template_name="index.html"))
  ```
- **Generated Template:** `frontend/dist/index.html` is copied to `templates/index.html` by `scripts/build.sh`. Any theme pre-initialization script must be injected into `frontend/index.html` so it persists during build.

---

## 3. Complete Route Map

| Route Path | Name / Key | Component | Auth Guard | Params & Query Handled | Description |
|---|---|---|---|---|---|
| `/login` | Login | `views/Login.vue` | Public (`meta.public = true`) | Query: `next` | User authentication via username & password. |
| `/` | Root | *Redirect* | Public | None | Redirects automatically to `/dashboard`. |
| `/dashboard` | Dashboard | `views/Dashboard.vue` | Protected | Currently internal state; receives `branch`, `customer`, `job_type`, `range`, `from`, `to` | Executive dashboard with KPIs, revenue/cost charts, attention items, billing, fleet health. |
| `/control-tower` | ControlTower | `views/ControlTower.vue` | Protected | Query: `branch` | Real-time operations tower for trips on road, departures, idle fleet, GPS pings. |
| `/orders/:id(\\d+)` | OrderDetail | `views/OrderDetail.vue` | Protected | Param: `id` (numeric) | Dedicated end-to-end order cockpit with status transitions, legs, and cargo details. |
| `/r/:key` | ResourceList | `views/ResourceList.vue` | Protected | Param: `key` (resource slug). Query: `search`, `status`, `page`, `page_size`, `ordering`, plus any registry filter keys (`branch`, `customer`, `[date]__gte`, etc.) | Generic data table driven by registry metadata. |
| `/r/:key/new` | ResourceCreate | `views/ResourceForm.vue` | Protected | Param: `key` | Multi-step / single-step form for creating new resources. |
| `/r/:key/:id(\\d+)` | ResourceDetail | `views/ResourceDetail.vue` | Protected | Params: `key`, `id` | Generic detail view displaying all fields in a card grid. |
| `/r/:key/:id(\\d+)/edit` | ResourceEdit | `views/ResourceForm.vue` | Protected | Params: `key`, `id` | Edit form pre-populated with existing record data. |
| `/configuration` | ConfigHub | `views/ConfigHub.vue` | Protected | Search query `q` (local) | Directory of all configuration master records. |
| `/:p(.*)*` | NotFound | `views/NotFound.vue` | Protected | Param: `p` | 404 fallback page. |

---

## 4. API Call Map (Regression Checklist)

Every API call listed below must remain **100% functional, byte-for-byte compatible in payload shape, method, and query parameters**:

| Endpoint | Method | Query Parameters | Request Payload | Response Shape | Used By Component(s) |
|---|---|---|---|---|---|
| `/api/auth/login/` | `POST` | None | `{ username, password }` | `{ access: string, refresh: string }` | `src/api.js` (called from `Login.vue`) |
| `/api/auth/refresh/` | `POST` | None | `{ refresh }` | `{ access: string, refresh?: string }` | `src/api.js` (Axios 401 interceptor) |
| `/api/auth/me/` | `GET` | None | None | `{ id, username, name, email, is_staff, display_tz }` | `src/api.js` (`loadMe()`, router guard) |
| `/api/meta/` | `GET` | None | None | `{ groups: Record<string, Array<{ key, title, icon }>>, countries: [...] }` | `App.vue`, `views/ConfigHub.vue` |
| `/api/meta/:key/` | `GET` | None | None | Resource metadata object (see Section 5) | `ResourceList.vue`, `ResourceDetail.vue`, `ResourceForm.vue` |
| `/api/:key/` | `GET` | `page`, `page_size`, `search`, `ordering`, `[filter_name]`, `[date]__gte`, `[date]__lte`, `[status_name]` | None | `{ count: number, next: string\|null, previous: string\|null, results: Array<Record<string, any>> }` | `ResourceList.vue`, `RefSelect.vue` (page_size=500) |
| `/api/:key/counts/` | `GET` | Same as `/api/:key/` except status filter is stripped | None | `{ [status_value]: number, all: number }` | `ResourceList.vue` |
| `/api/:key/export/` | `GET` | Same as `/api/:key/` (excluding pagination `page`/`page_size`) | None (responseType: `blob`) | CSV binary file stream | `ResourceList.vue` |
| `/api/:key/:id/` | `GET` | None | None | Object containing field values and `[field]_label` helpers | `ResourceDetail.vue`, `ResourceForm.vue` |
| `/api/:key/` | `POST` | None | Object with field values (`null` for empty) | Created object with assigned `id` | `ResourceForm.vue` |
| `/api/:key/:id/` | `PATCH` | None | Object with changed field values | Updated object | `ResourceForm.vue` |
| `/api/:key/:id/` | `DELETE` | None | None | 204 No Content | `ResourceDetail.vue` |
| `/api/orders/:id/full/` | `GET` | None | None | Order object + embedded `trips`, `vendor_orders`, `invoices`, `next_statuses`, `lane_detail` | `views/OrderDetail.vue` |
| `/api/orders/:id/transition/` | `POST` | None | `{ status: string }` | Returns updated full order object (`full()` serializer) | `views/OrderDetail.vue` |
| `/api/drivers/:id/set_passcode/` | `POST` | None | `{ passcode: string }` | `{ ok: true, passcode_set_at: string }` | `views/ResourceDetail.vue` |
| `/api/reports/:id/download/` | `GET` | None | None (responseType: `blob`) | CSV binary file stream | `views/ResourceDetail.vue` |
| `/api/dashboard/` | `GET` | `range` (`7d`\|`30d`\|`90d`\|`mtd`), `from`, `to`, `branch`, `customer`, `job_type` | None | Complex dashboard aggregate object: `{ period, currency, kpis, series, funnel, attention, finance, commercial, fleet, top_customers, by_job_type, lanes, branches }` | `views/Dashboard.vue` |
| `/api/control-tower/` | `GET` | `branch` (optional) | None | `{ updated_at, tiles: { on_road, at_risk, need_truck, gps_silent, idle }, on_road: [...], departures: [...], idle_vehicles: [...] }` | `views/ControlTower.vue` |
| `/api/health/` | `GET` | None | None | `{ ok: true, time: string }` | Global health monitor |

---

## 5. Registry-Driven Architecture & Metadata Shape

The entire application relies on `core/registry.py` metadata exposed via `GET /api/meta/:key/`. The frontend receives an object with this exact shape:

```typescript
interface ResourceMeta {
  key: string;              // e.g. "orders", "trips", "vehicles"
  title: string;            // e.g. "Orders", "Trip scheduling"
  group: string;            // e.g. "Operations", "Rates", "Fleet", "Configuration"
  icon: string;             // emoji e.g. "📦", "🗓️"
  columns: string[];        // Default column order e.g. ["number", "customer", "status", ...]
  fields: Record<string, FieldMeta>;
  filters: FilterMeta[];
  dates: Array<{ name: string; label: string }>;
  status: string | null;    // Name of status field, e.g. "status"
  status_choices: Array<{ value: string; label: string }> | null;
  steps: Array<{ title: string; fields: string[] }> | null;
  search: boolean;          // True if backend supports search filter
  detail: boolean;          // True if custom detail view exists
  create: boolean;          // True if resource allows creation
}

interface FieldMeta {
  name: string;
  label: string;
  type: "char" | "text" | "int" | "decimal" | "bool" | "datetime" | "date" | "email" | "choice" | "fk" | "m2m" | "computed";
  help: string;
  required: boolean;
  readonly: boolean;
  choices?: Array<{ value: string | number; label: string }>;
  resource?: string;        // Target resource key if fk or m2m (e.g. "customers", "branches")
  money?: boolean;          // Flagged true for rate/currency decimal fields
}

interface FilterMeta {
  name: string;             // e.g. "customer" or "lane__source"
  label: string;
  type: string;
  choices?: Array<{ value: string | number; label: string }>;
  resource?: string;
}
```

### Serializer Output Convention
Every record serialized by Django REST Framework in this system provides:
1. Raw value at `row[fieldName]` (e.g. `row.customer = 14`, `row.status = "in_progress"`).
2. Human-readable display label at `row[fieldName + "_label"]`:
   - For ForeignKeys: String representation of related model (e.g. `row.customer_label = "Emirates Steel LLC"`).
   - For Choices: Choice label (e.g. `row.status_label = "In progress"`).
   - For ManyToMany: Array of string labels.
3. String representation of the entire object at `row.display`.

---

## 6. Component Inventory & Replacement Strategy

| Existing Component | Current Role | Shortcomings | Target Replacement |
|---|---|---|---|
| `App.vue` | Root frame with sidebar, mobile drawer toggle, live clock, user menu | Hardcoded brand blue, no theme toggle, raw layout, no breadcrumbs, emoji navigation. | `src/layouts/AppShell.vue` with `Sidebar.vue`, `Topbar.vue`, `CommandPalette.vue` (`reka-ui` Dialog + `fuse.js`). |
| `components/Cell.vue` | Formats table cells based on field type | Inline ternary spaghetti, emojis, no tabular-nums, no copy-to-clipboard, lacks tooltip for truncated text. | Modular TanStack cell renderers in `src/components/data-table/cells/` (`StatusCell`, `MoneyCell`, `DateCell`, `IdCell`, `WeightCell`, `EntityCell`, `LinkCell`). |
| `components/FieldInput.vue` | Form input renderer | Native `<input>` and `<select>`, missing accessibility attributes (`aria-describedby`), errors displayed in raw red paragraph. | `src/components/ui/FormField.vue` composing dedicated primitives: `Input`, `Select`, `Combobox`, `MultiSelect`, `DatePicker`, `Switch`, `Textarea`. |
| `components/RefSelect.vue` | Select for FK / M2M relationships | Dumps up to 500 options into raw `<select>` via global `window.__refCache`; no search, no debounce, unstyled multiple select. | `src/components/ui/Combobox.vue` & `MultiSelect.vue` using `reka-ui` Combobox with debounced async queries, abort controller, and recent items. |
| `views/Login.vue` | Basic login form | Plain blue gradient, centered card, basic inputs, lacks caps-lock warning, no animation or brand storytelling. | Split-screen layout: interactive animated SVG route-map with moving truck + mesh gradient on left; glassmorphism login card with floating labels on right. |
| `views/Dashboard.vue` | Analytics dashboard | Fixed Chart.js charts, hardcoded hex colors, no container queries, raw tables without pagination or proper alignment. | Redesigned dashboard with sticky filter bar, token-themed KPI cards with sparklines, modular `vue-echarts`, independent skeleton/error states. |
| `views/ControlTower.vue` | Real-time operations board | Polling continues when tab hidden, basic list layout, minimal visual hierarchy for risks. | Live Kanban / Operational Board with trip cards, delay badges, animated auto-refresh indicator with pause/resume and visibility detection. |
| `views/OrderDetail.vue` | Order detail page | Simple grid of raw cards and unstyled table. | Order Operations Center: interactive status tracker, allocation summary, route map card placeholder (`RouteMap.vue`), legs table, cargo chips. |
| `views/ResourceList.vue` | Master data table | Monolithic file with manual pagination, basic filtering, no column resizing or drag reorder, no bulk actions. | TanStack-powered `ResourceList.vue` + `DataTable.vue` + `DataTableToolbar.vue` + `DataTableFilters.vue` (slide-over) + `DataTableColumnChooser.vue` + `DataTableBulkBar.vue` + `ResourceQuickView.vue`. |
| `views/ResourceDetail.vue` | Generic resource detail | 2-column description grid, raw delete confirmation. | Structured `ResourceDetail.vue` with sticky header, copyable mono ID, status pill, tabs, quick facts sidebar, promise-based confirm dialog. |
| `views/ResourceForm.vue` | Generic create/edit form | Simple steps, errors shown at the bottom in a red box, no validation on blur, no draft autosave. | Wizard/Single-form experience with vee-validate + zod, error summary with click-to-focus, smart dependent fields, autosave drafts, dirty form guard. |
| `views/ConfigHub.vue` | Configuration directory | Minimal card grid. | Modern categorized configuration directory with live search and status indicators. |
| `views/NotFound.vue` | 404 page | Generic box with emoji. | Styled `EmptyState` component with helpful navigation actions. |

---

## 7. Status Vocabulary & Semantic Mapping

An exhaustive audit of all choices across backend models revealed **38 distinct status values**. Below is their semantic tone mapping for `src/design/status.js`:

| Status Key | Display Label | Semantic Tone | Associated Modules | Icon / Visual Indicator |
|---|---|---|---|---|
| `active` | Active | `success` | Orders, Trips, Contracts, Vehicles, Drivers, Branches | CheckCircle2 |
| `completed` | Completed | `success` | Orders, Trips, Maintenance, Bids, AssetTransfers | CheckCheck |
| `delivered` | Delivered | `success` | Orders, Trips | PackageCheck |
| `paid` | Paid | `success` | Invoices, Allowances | BadgeCheck |
| `accepted` | Accepted | `success` | Maintenance, Quotations | Check |
| `approved` | Approved | `success` | RateInquiries | ThumbsUp |
| `sourced` | Sourced | `success` | Sourcing | Sparkles |
| `used` | Used | `success` | GatePasses | History |
| `in_progress` | In progress | `accent` (live) | Trips, JobCards | PlayCircle (pulse dot) |
| `in_transit` | In transit | `accent` (live) | Orders, Trips | Truck (pulse dot) |
| `on_road` | On the road | `accent` (live) | Control Tower | Navigation (pulse dot) |
| `in_use` | In use | `accent` | Trailers | Cog |
| `issued` | Issued | `info` | MaterialRequests, GatePasses | Send |
| `sent` | Sent | `info` | Quotations | Send |
| `sourcing` | Sent to sourcing | `info` | RateInquiries | Search |
| `confirmed` | Confirmed | `info` | Orders | ShieldCheck |
| `assigned` | Assigned | `info` | Trips, JobCards | UserCheck |
| `scheduled` | Scheduled | `info` | RFQs, Maintenance | Calendar |
| `bid_created` | Bid created | `info` | Sourcing | FilePlus |
| `ready_for_invoice` | Ready for invoice | `info` | Orders | Receipt |
| `invoiced` | Invoiced | `info` | Orders, Invoices | FileText |
| `generated` | Generated | `info` | Reports | BarChart3 |
| `available` | Available | `neutral` | Trailers | CheckSquare |
| `pending` | Pending | `neutral` | Orders, Maintenance, Contracts, Bids | Clock |
| `pending_approval` | Pending approval | `neutral` | RateInquiries | Clock4 |
| `draft` | Draft | `neutral` | Quotations, Invoices, RFQs | FileEdit |
| `created` | Created | `neutral` | Orders, Trips | PlusCircle |
| `requested` | Requested | `neutral` | AssetTransfers, MaterialRequests | HelpCircle |
| `open` | Open | `neutral` | JobCards, Sourcing | FolderOpen |
| `closed` | Closed | `neutral` | Maintenance, RFQs | FolderCheck |
| `unassigned` | Needs a truck | `warning` | Trips | AlertTriangle |
| `on_hold` | On hold | `warning` | JobCards | PauseCircle |
| `maintenance` | In maintenance | `warning` | Vehicles, Trailers | Wrench |
| `on_lease` | On lease | `warning` | Vehicles, Trailers, LeaseOrders | Key |
| `disputed` | Disputed | `warning` | Invoices | AlertCircle |
| `cancelled` | Cancelled | `danger` | Orders, Trips, Sourcing, AssetTransfers | XCircle |
| `rejected` | Rejected | `danger` | Quotations, RateInquiries, MaterialRequests | Ban |
| `expired` | Expired | `danger` | Quotations, Contracts, Documents, RFQs | ClockAlert |
| `failed` | Failed | `danger` | Trips, Payouts | AlertOctagon |
| `inactive` | Inactive / Deactivated | `neutral` | Drivers, Vehicles, Branches, Customers | MinusCircle |
| `void` | Void | `danger` | GatePasses | FileX |

*Any unrecognized status string safely defaults to `tone: 'neutral'` with automated title-casing.*

---

## 8. Current UX Problems Identified

1. **Inconsistent Vertical Rhythm & Mismatched Controls:**
   - Controls in toolbar rows feature mixed heights: inputs are 38px, native selects are 38px, button links are 36px, and pagination selects are arbitrarily styled with `!py-1`.
   - Ad-hoc utility overrides (`!w-44`, `!w-48`, `!w-36`, `!w-20`) cause awkward responsive wrapping and jagged margins.
2. **Poor Dropdown & Foreign Key Experience:**
   - `RefSelect.vue` loads up to 500 records into a raw `<select>` element without search or autocomplete. On high-volume entities (e.g. Orders, Vehicles, Customers), finding a record requires scrolling through hundreds of options.
   - For `m2m` fields, `RefSelect` renders a raw browser multi-select box (`<select multiple class="h-32">`) which is unintuitive and error-prone.
3. **Flawed Loading & Empty States ("0 of 0" Glitches):**
   - While requests are in flight, tables display "0 records" and pagination shows "0 of 0", giving users the impression data is missing before the response arrives.
   - Skeletons are generic gray pulsing rectangles that jump in size when real data renders.
   - Empty states for filtered results lack a "Clear filters" call-to-action.
4. **Table Density & Data Usability Deficits:**
   - Tables lack column resizing, column reordering, density toggles, row selection, and bulk action bars.
   - Text truncation is abrupt without tooltips, and numbers (currency, weights, dates) lack tabular numerical formatting, causing columns to misalign visually.
   - No sticky columns for IDs or row actions; horizontal scrolling leaves records without visual context.
5. **Mobile Responsiveness Deficiencies:**
   - Large tables simply overflow horizontally with standard browser scrollbars. No responsive card list mode exists for screens under 768px.
   - Modals and drawers are nonexistent; everything renders as inline page blocks.
   - The mobile sidebar lacks proper backdrop focus management and closing animations.
6. **Accessibility & Contrast Vulnerabilities:**
   - Multiple badges use color combinations that fail WCAG AA contrast (e.g., `bg-amber-100 text-amber-800` is borderline; `bg-rose-50 text-rose-600` fails against white cards).
   - Interactive elements lack visible `:focus-visible` keyboard rings.
   - Form inputs lack `aria-invalid`, `aria-describedby`, and associated screen-reader announcements.
7. **Lack of Dark Mode & Modern Polish:**
   - No dark theme exists. Colors are hardcoded with Tailwind's `slate` and `brand` scales directly in component classes.
   - Heavy reliance on inline emojis ("🚚", "📈", "⚙️") detracts from an enterprise B2B SaaS feel.

---

## 9. Migration Roadmap (Phase 1 to Phase 10)

- **Phase 1: Foundations & Design Tokens**
  - Install dependencies (`reka-ui`, `@tanstack/vue-table`, `lucide-vue-next`, `clsx`, `tailwind-merge`, `class-variance-authority`, `@fontsource-variable/inter`, `@fontsource-variable/jetbrains-mono`, `@vueuse/core`, `date-fns`).
  - Create `src/design/tokens.css`, `src/design/tailwind-preset.js`, `src/design/status.js`, and `src/design/index.md`.
  - Establish `useTheme` composable with light/dark/system modes and zero-flash inline script.
  - Set up `/ui-kit` development route.
- **Phase 2: UI Primitives & Form Controls**
  - Implement accessible headless primitives: `Button`, `Input`, `Textarea`, `Select`, `Combobox`, `MultiSelect`, `DatePicker`, `DateRangePicker`, `Checkbox`, `Switch`, `Badge`, `StatusPill`, `Card`, `Modal`, `Drawer`, `Toast`, `Skeleton`, `EmptyState`.
  - Showcase all variants, states, and themes in `/ui-kit`.
- **Phase 3: Application Shell & Navigation**
  - Build modern `AppShell`, collapsible `Sidebar` (persisted in `localStorage`), sticky `Topbar`, and `CommandPalette` (`⌘K`).
- **Phase 4: DataTable & Registry-Driven ResourceList**
  - Build `DataTable.vue` on TanStack Table with toolbar, filter slide-over, column chooser, density toggle, resizable columns, sticky columns, and formatted cell renderers.
  - Wire existing registry metadata into `ResourceList.vue` with URL synchronization.
- **Phase 5: Forms & Wizards**
  - Rebuild `ResourceForm.vue` with vee-validate + zod, step wizards, error summary with scroll-to-field, async FK comboboxes, unit suffixes, draft autosave, and unsaved changes guards.
- **Phase 6: Detail Views**
  - Rebuild `ResourceDetail.vue` and `OrderDetail.vue` with copyable mono IDs, status timeline, allocation summaries, route map card, and tabs.
- **Phase 7: Dashboard Overhaul**
  - Migrate charts to tree-shaken `echarts` + `vue-echarts`. Implement themed KPI cards with sparklines and directional deltas.
- **Phase 8: Control Tower**
  - Build live kanban board with delay badges, trip cards, quick-view slideover, and tab-visibility-aware auto-polling.
- **Phase 9: Interactive Login Experience**
  - Build split-screen login with animated SVG route-map and mesh gradient on left; glassmorphism login card with floating labels, caps-lock warning, error shake, and smooth transition on right.
- **Phase 10: Verification & Cleanup**
  - Full accessibility audit, responsive pass (1440px, 1024px, 375px), bundle size profiling, removal of obsolete CSS and components. Verify `scripts/build.sh` produces zero errors.
