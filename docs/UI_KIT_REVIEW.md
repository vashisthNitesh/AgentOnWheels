# AgentOnWheels /ui-kit Review (dark/system theme, 1440px + 390px)

## P1 – Bugs / broken components
1. **Mobile page-wide horizontal overflow** (whole page, 390px). The H1 is clipped ("UI Primitiv…"), the theme switcher, cards and the "Ghost" button run off the right edge. Something wider than the viewport (DataTable, the underline Tabs, Stepper or Pagination) widens the document. Fix: on the root (L2) use `overflow-x-hidden` as a guard, and do the real fix by wrapping DataTable in `<div class="overflow-x-auto -mx-6 px-6">`. Give Tabs and Stepper `overflow-x-auto whitespace-nowrap`, and give the H1 (L14) `break-words text-2xl sm:text-3xl`.
2. **Password field not in a form** (console `[DOM] Password field is not contained in a form`). Driver Passcode (L97-99). Fix: wrap the form grid (L85-154) in `<form @submit.prevent autocomplete="off">`, and set `autocomplete="new-password"` and `inputmode="numeric"` on the Input. Passcodes are digits, per the error text.
3. **Selected DataTable rows use light-mode colours in dark mode.** Rows 1-2 get a light-grey background, so the white and mono text loses contrast (well under AA). The bug is in DataTable.vue's selected-row class. Fix: `bg-primary-50 dark:bg-primary-950/40` plus a left `border-l-2 border-primary-500`. Don't use a plain light-only gray.
4. **Stepper error step ("Route Scheduling") renders as a white pill** in dark mode, and its icon is just a dark blob. Fix in Stepper.vue: `bg-danger-50 dark:bg-danger-950/40 text-danger-600 dark:text-danger-400 ring-1 ring-danger-500/40`, with an `AlertCircle` icon.
5. **Cargo Weight `suffix="tonnes"` is not rendered** (L88). Only the clear X shows. Input.vue either ignores `suffix` or the clear button replaces it. Render the suffix slot next to the clear button, and use "t" to match the table.
6. **The "AED" prefix runs into the value** ("AED1850.00", L93). Fix in Input.vue: give the prefix its own padding (`pl-12` on the input, or a flex addon with a border-r), and format the value as `1,850.00`.
7. **The indeterminate checkbox shows a solid filled square with no dash** (L161). Fix in Checkbox.vue: when `modelValue==='indeterminate'`, set `el.indeterminate=true` and render a `Minus` icon. Also set `aria-checked="mixed"`.
8. **The StatusPill vocabulary is missing statuses.** `delivered` and `pending` (table rows 3-4) render as generic neutral or green pills with no icons, and the demo row uses `unassigned` labelled "Needs a truck". Add `delivered`, `pending` and the other backend statuses to the StatusPill tone/icon map so the table and pills stay consistent.
9. **DataTableBulkBar is fixed at the bottom of a very tall empty page.** The screenshot shows about 2,500px of blank space after the table, with the bar floating at the bottom. Make the bar `fixed bottom-6 inset-x-0 mx-auto w-fit`, which it partly is now. Then work out what adds the extra min-height: probably a `min-h-screen` on a nested wrapper or an unclosed Teleport/Drawer placeholder. Hide the bar with `v-if="selectedCount"`, and on mobile reserve space with `pb-24`.
10. **Muted text is unreadable.** Loading At values in the table, "Disabled State", the KPI sub-labels, and the "Optional" and "56 / 300" counter text are about #4b5563 on #0b1220, roughly 2.5:1. Raise `text-muted` in dark mode to about slate-400 (#94a3b8, about 5:1).
11. **Wrong button label.** The loading buttons show "Saving Changes…" while the spinner already signals the state. That's fine, but `loading` buttons should also get `aria-busy` and `disabled`. Check Button.vue.
12. **Timestamps don't match.** The drawer hardcodes "Planned Pickup 20 Oct 2026, 08:30" (L483), while the table and DatePicker show the same 08:30Z as 12:30 (Asia/Dubai). Use the shared formatter (`formatDateTime(row.loading_at)`) in the drawer.
13. **`openQuickView(row)` ignores the row** (L655). The drawer always shows ORD-2026-9041. Store `quickRow.value=row` and bind the title and fields to it.
14. **Avatar `size="40"` is passed as a string** (L266-271, L383). If the component expects a Number or a token, use `:size="40"`.
15. **Textarea `maxlength="300"` is a string** (L152). Use `:maxlength="300"` so the counter logic compares numbers.

## P2 – Accessibility
- The theme switcher (L19-34) needs `role="radiogroup"` with `role="radio"` and `aria-checked` on each button, or `aria-pressed`. Same for the Density toggle (L428-440), which also lacks `focus-ring` and `type="button"`.
- All raw `<button>` elements need `type="button"` (L20, L429). Once the form wrapper from fix #2 is in place, they would otherwise submit the form.
- The icon-only Settings button (L64) uses `title` only. Add `aria-label="Settings"`.
- The "Driver Passcode" `hint` is overridden by `error` and never shows. Link both through `aria-describedby`, and make sure FormField sets `aria-invalid` and `role="alert"` on the error.
- The emoji in the H2s (L40, 82, 184…) are read aloud by screen readers. Wrap them in `<span aria-hidden="true">`, or replace them with lucide icons.
- The table checkboxes need `aria-label="Select ORD-2026-9041"`. The kebab "…" button needs `aria-label="Row actions"`. Sortable headers need `aria-sort`.
- Rows open the drawer on click (`@row-click`). Make them keyboard-reachable (`tabindex=0`, Enter opens it) and move focus into the drawer.
- The live pulse on StatusPill should respect `motion-reduce:animate-none`.
- Kbd shows ⌘ to everyone. Detect the platform and show "Ctrl" on Windows and Linux.
- The section labels ("VARIANTS", etc.) are tiny mono text in muted colour (see #10). Use `text-[11px]` at minimum with a stronger tone.

## P3 – Responsive / mobile
- Fix the overflow first (#1).
- The theme switcher should be `w-fit self-start` on mobile, not full width.
- The Overlays button row should stack as `grid grid-cols-2 gap-2 sm:flex` on mobile.
- Pagination wraps poorly: "Showing 1–20 of 1,284" is cut off. Use `flex-col sm:flex-row` and hide "Rows per page" text below `sm`.
- In the table on mobile, Order # wraps to 3 lines. Add `whitespace-nowrap` to the ID and date cells and keep the table scrolling horizontally, or switch to a card list below `md`, with a sticky first column.
- The Stepper should become vertical, or "Step 2 of 4" plus a progress bar, below `sm`.
- The Tabs ("Legs & Trips 3" wraps onto 2 lines) need a horizontal scroll strip with fade edges.
- The page header (L8) and density row (L422) should be `flex-wrap gap-3`.
- Reduce padding from `p-6` to `p-4 sm:p-6` on cards, since the root already has `p-6`.

## P4 – Visual design enhancements
- Section rhythm: `space-y-14` with full cards creates a lot of dead space. Use a sticky left table of contents (anchor nav) for the kit on desktop, and give each section a short description.
- The section headings mix emoji with "Phase 4:" labels. Drop the phase labels and use consistent lucide icons in a tinted square.
- The Buttons card: the "Large" button looks only slightly larger. Show sizes side by side with labels underneath. Small buttons in primary only; show secondary sizes too. Give the disabled button `opacity-50 cursor-not-allowed` so it doesn't look like Ghost.
- The Avatars card is mostly empty space. Add size and status-dot variants, and lay it out as a 2-column grid of "micro components" (Copy, Kbd, Divider, Tooltip demo — Tooltip is imported at L529 but never used).
- KPI cards: the delta and subtitle compete on one line. Put the subtitle on its own line, and give the sparkline an area gradient fill and tone colour (red for a bad trend). Show the hover/clickable affordance with a chevron.
- Badges: the semantic badges and status pills look alike. Make Badges flatter, with no border.
- Skeletons should shimmer (a `bg-gradient` animate), and the three demos should look like real content (table row, KPI, list).
- The EmptyState icon tile is low contrast. Use the tone colour background `bg-warning-500/10`.
- Table: add a toolbar demo (search, filter chips, column chooser, export) so it matches the target ListView. Use zebra or hover rows, right-align money in mono with a muted currency code ("AED" muted, number bold), and add a sort indicator on hover for all sortable headers.
- Add a light-mode screenshot pass. Several of the bugs above (#3, #4) come from light-only classes, so test every component in both themes.
