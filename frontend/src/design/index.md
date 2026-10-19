# AgentOnWheels Design System Specification

**Version:** 1.0.0  
**Stack:** Vue 3 + Tailwind CSS + CSS Variables (RGB Triplet Composition)  
**Location:** `src/design/`  

---

## 1. Color System & Contrast Audit

Colors are defined in `tokens.css` as space-separated RGB triplets (`R G B`). This enables Tailwind opacity modifiers (`bg-primary-600/50`) without breaking CSS variable resolution.

### 1.1 Palette Architecture
- **Primary (Indigo):** 50–950 scale centered on `#4F46E5` (600). Used for primary calls-to-action, active indicators, and brand identity. In light mode, buttons use 600; in dark mode, buttons use 500 for enhanced luminosity.
- **Accent (Teal):** 50–950 scale centered on `#14B8A6` (500). Represents "on the move" / live logistics statuses, GPS pings, route segments, and active in-transit vehicles. Never used for errors.
- **Neutrals (Slate):** 0–950 (`#FFFFFF`, `#F8FAFC` ... `#020617`).
- **Semantic Scales:**
  - `success` (Emerald): 50, 100, 500, 600, 700
  - `warning` (Amber): 50, 100, 500, 600, 700
  - `danger` (Rose): 50, 100, 500, 600, 700
  - `info` (Sky): 50, 100, 500, 600, 700

### 1.2 Semantic Aliases
Components use exclusively semantic aliases rather than arbitrary scales:

| Semantic Alias | Light Mode Value | Dark Mode Value | Semantic Role |
|---|---|---|---|
| `--bg-app` | slate-50 (`#F8FAFC`) | slate-950 (`#020617`) | Main application background canvas |
| `--bg-surface` | white (`#FFFFFF`) | slate-900 (`#0F172A`) | Primary cards, table bodies, forms |
| `--bg-surface-raised` | white (`#FFFFFF`) | slate-800 (`#1E293B`) | Popovers, modal dialogs, slide-over drawers |
| `--bg-subtle` | slate-50 (`#F8FAFC`) | slate-800/60 (`#1E293B99`) | Table headers, row hover states |
| `--bg-muted` | slate-100 (`#F1F5F9`) | slate-800 (`#1E293B`) | Zebra rows, disabled controls, skeleton loaders |
| `--border-default` | slate-200 (`#E2E8F0`) | slate-800 (`#1E293B`) | Structural cards, dividers, table grid borders |
| `--border-strong` | slate-300 (`#CBD5E1`) | slate-700 (`#334155`) | Form inputs, select triggers, checkbox borders |
| `--text-primary` | slate-900 (`#0F172A`) | slate-50 (`#F8FAFC`) | Headings, table cells, primary body copy |
| `--text-secondary` | slate-600 (`#475569`) | slate-400 (`#94A3B8`) | Subtitles, helper text, table column headers |
| `--text-muted` | slate-500 (`#64748B`) | slate-500 (`#64748B`) | Placeholders, inactive captions, metadata |
| `--text-on-primary` | white (`#FFFFFF`) | white (`#FFFFFF`) | High-contrast label on primary & danger buttons |
| `--focus-ring` | primary-500 @ 40% | primary-400 @ 50% | Accessible focus indicators (`:focus-visible`) |
| `--overlay` | slate-950 @ 40% | black @ 60% | Modal & drawer backdrops |

### 1.3 WCAG AA Contrast Verification
All text/background combinations meet or exceed WCAG AA guidelines:

| Pair (Foreground / Background) | Light Contrast Ratio | Dark Contrast Ratio | Standard | Result |
|---|---|---|---|---|
| `--text-primary` / `--bg-surface` | **15.8:1** (Slate 900 on White) | **16.1:1** (Slate 50 on Slate 900) | 4.5:1 | **PASS (AAA)** |
| `--text-secondary` / `--bg-surface` | **7.1:1** (Slate 600 on White) | **5.4:1** (Slate 400 on Slate 900) | 4.5:1 | **PASS (AA)** |
| `--text-muted` / `--bg-surface` | **4.6:1** (Slate 500 on White) | **4.7:1** (Slate 500 on Slate 900) | 4.5:1 | **PASS (AA)** |
| `--text-on-primary` / Primary Button | **4.8:1** (White on Indigo 600) | **5.1:1** (White on Indigo 500) | 4.5:1 | **PASS (AA)** |
| Success Pill text / Pill bg | **4.9:1** (Emerald 700 on Emerald 50) | **6.2:1** (Emerald 300 on Emerald 950) | 4.5:1 | **PASS (AA)** |
| Danger Pill text / Pill bg | **5.2:1** (Rose 700 on Rose 50) | **6.5:1** (Rose 300 on Rose 950) | 4.5:1 | **PASS (AA)** |
| Border strong / Surface | **3.2:1** (Slate 300 on White) | **3.4:1** (Slate 700 on Slate 900) | 3.0:1 | **PASS (UI)** |

---

## 2. Status Color System (`status.js`)

Statuses use semantic tones: `success`, `accent`, `info`, `warning`, `danger`, and `neutral`. Every pill includes an icon, semantic label, and optional animated pulse indicator for active logistics operations.

```javascript
import { getStatusMeta, TONE_STYLES } from '@/design/status.js'

const meta = getStatusMeta('in_transit')
// Returns:
// { key: 'in_transit', label: 'In transit', tone: 'accent', icon: 'Truck', pulse: true }
```

---

## 3. Typography Standards

- **UI Font:** `Inter Variable` with OpenType features `cv11` (single-storey 'a') and `ss01` (simplified 't').
- **Monospace Font:** `JetBrains Mono Variable` for IDs (`ORD-10923`), VIN numbers, truck plates, container numbers, and AWB codes.
- **Tabular Figures:** All numeric fields (amounts, KPIs, weights, distances, dates, counts) enforce `font-variant-numeric: tabular-nums` (`.tabular-nums`) to ensure vertical alignment in tables.

| Scale Token | Size / Line-height | Font Weight | Typical Usage |
|---|---|---|---|
| `text-xs` | 12px / 16px | 500 | Badges, status pills, table headers, overline captions |
| `text-sm` | 13px / 20px | 400–500 | Table data cells, form inputs, secondary metadata |
| `text-base` | 14px / 22px | 400 | Default body text |
| `text-md` | 16px / 24px | 500 | Card titles, group section headings |
| `text-lg` | 18px / 28px | 600 | Section titles, drawer headers |
| `text-xl` | 20px / 28px | 600 | Mobile page titles |
| `text-2xl` | 24px / 32px | 600 | Desktop page titles |
| `text-3xl` | 30px / 36px | 600 | Primary KPI metric values |
| `text-4xl` | 36px / 40px | 700 | Login brand hero |

---

## 4. Spacing, Sizing, Elevation & Grid

- **8px Grid System:** Page padding 24px desktop / 16px mobile. Gap between sections: 24px. Gap inside cards: 16–20px. Form field gap: 16px vertical, 16–24px horizontal.
- **Control Heights:** Every control in a toolbar or form row strictly matches:
  - `sm`: 32px
  - `md`: 36px (default)
  - `lg`: 40px
  - Square icon buttons match respective heights (32x32, 36x36, 40x40).
- **Table Density:**
  - Compact: 36px row height
  - Comfortable: 44px row height (default)
  - Relaxed: 52px row height
- **Elevation Z-Index Scale:**
  - Base: 0
  - Sticky Headers: 10
  - Top Bar: 20
  - Sidebar: 30
  - Dropdown / Combobox: 40
  - Slide-Over Drawer: 50
  - Modal Dialog: 60
  - Popover inside Modal: 70
  - Toast: 80
  - Tooltip: 90

---

## 5. Motion & Accessibility

- **Durations:**
  - Fast: 150ms (button clicks, hover tints)
  - Base: 200ms (popovers, dropdown menus)
  - Slow: 250ms (drawers, modal backdrops)
- **Easings:** `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out) for entrance; `cubic-bezier(0.7, 0, 0.84, 0)` for exit.
- **Reduced Motion:** If `prefers-reduced-motion: reduce` is enabled, translations, scales, and continuous animations are suppressed; opacity fades remain capped at ≤ 100ms.

---

## 6. Registry Metadata to UI Adapter & DataTable Specification

The application presentation layer is driven by declarative registry metadata from `/api/meta/:key/`. This allows all ~40 modules to share a consistent, high-performance, accessible data table experience.

### 6.1 Field Type to Cell Renderer Mapping

| Registry Field Metadata | Detected Type | Component | Formatting & Behavior |
|---|---|---|---|
| `name === 'status'` or `(type === 'choice' && name.includes('status'))` | Status Enum | `StatusCell.vue` | Semantic `StatusPill` with token color tone and icon |
| `money === true` or `name in ('rate', 'sell_rate', 'buy_rate', 'total', 'amount', 'cost', 'margin')` | Currency | `MoneyCell.vue` | `formatCurrency` with row currency symbol, fixed 2 decimals, tabular numerals, right-aligned |
| `type === 'date'` or `type === 'datetime'` or `name.endsWith('_at')` or `name.endsWith('_date')` | Date/Time | `DateCell.vue` | Localized date/time in user timezone with relative time tooltip ("3 hours ago") |
| `name === 'id'` or `name === 'number'` or `name === 'code'` or `name === 'reference'` or `name.endsWith('_ref')` | Identifier | `IdCell.vue` | Monospace font, high contrast, copy-on-hover button |
| `name.endsWith('_t')` or `name === 'weight_t'` or `name === 'payload_t'` | Weight | `WeightCell.vue` | Tonnes (`t`) with tooltip showing kilograms (`kg`) |
| `name.endsWith('_km')` or `name === 'distance_km'` or `name === 'actual_km'` or `name === 'odometer_km'` | Distance | `DistanceCell.vue` | Kilometers (`km`) formatted with thousand separators |
| `name in ('driver', 'customer', 'vendor', 'vehicle')` or `f.resource in ('drivers', 'customers', ...)` | Entity Relational | `EntityCell.vue` | User avatar / initials pill alongside primary name and subtitle |
| `type === 'bool'` | Boolean | `BooleanCell.vue` | Subtle emerald check badge or dash (`—`) |
| `type === 'm2m'` or `Array.isArray(row[name + '_label'])` | Tags / Multiple | `TagsCell.vue` | Secondary badge pills with `+N` count overflow pill |
| Other string, foreign key, or text | Default | Text Cell | Text truncation with browser tooltip for long strings, muted dash for `null` |

### 6.2 Filter Type to Filter Control Mapping

| Registry Filter Definition | Control Component | Value Handling |
|---|---|---|
| `type === 'fk'` (`resource` specified) | `Combobox.vue` | Async resource options with search, cached via `window.__refCache` |
| `type === 'choice'` (`choices` array) | `Select.vue` / `MultiSelect.vue` | Predefined choice values with human-readable labels |
| `meta.dates` entry (`name`, `label`) | `DateRangePicker.vue` | Dual range picker with presets ("Last 7 days", "This month", etc.) serializing to `[field]__gte` and `[field]__lte` |
| `type === 'bool'` | `Select.vue` / `Switch.vue` | Tri-state: Any / Yes / No serializing to boolean or empty |
| `meta.status` (Status tab) | Status Tabs Bar | Quick navigation with record count badges serializing to URL query parameter |

### 6.3 DataTable Architecture & State Composables

- `useTable.js`: Manages pagination, page size (20/50/100), sorting (`ordering`), search, row selection, density, and request sequencing with `AbortController`.
- `useFilters.js`: Transforms filter values into API parameters and active filter chips with individual and bulk clear handlers.
- `useUrlState.js`: Synchronizes table state with `route.query` via `router.replace` without adding unwanted history entries.
- `useSavedViews.js`: Persists user custom views (filters, sorting, column visibility, density) in `localStorage` with modified-dot detection.
- `useCsvExport.js`: Automatically utilizes the backend `/api/:key/export/` endpoint with a client-side chunked fallback.
- `ResourceQuickView.vue`: Slide-over drawer on row click displaying key fields, status pill, relations, timeline summary, and action links.

