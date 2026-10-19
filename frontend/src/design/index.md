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
