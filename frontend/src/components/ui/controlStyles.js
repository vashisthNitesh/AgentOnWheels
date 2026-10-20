/**
 * Shared visual language for every form control (Input, Select, Combobox,
 * MultiSelect, DatePicker, DateRangePicker, Textarea) so heights, borders,
 * focus and error states are identical across the app.
 */

export const controlSizes = {
  sm: 'h-8 text-xs px-2.5 rounded-md',
  md: 'h-9 text-sm px-3 rounded-lg',
  lg: 'h-11 text-sm px-3.5 rounded-lg',
}

export const controlBase =
  'w-full bg-surface text-primary border shadow-xs transition-[border-color,box-shadow,background-color] duration-150 placeholder:text-muted outline-none'

export const controlIdle =
  'border-border-strong hover:border-slate-400 dark:hover:border-slate-500 ' +
  'focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15 ' +
  'focus-visible:border-primary-500 focus-visible:ring-4 focus-visible:ring-primary-500/15 ' +
  'dark:focus:ring-primary-400/20'

export const controlOpen = 'border-primary-500 ring-4 ring-primary-500/15 dark:ring-primary-400/20'

export const controlInvalid =
  'border-danger-500 hover:border-danger-500 focus:border-danger-500 focus:ring-4 focus:ring-danger-500/15 ring-danger-500/15'

export const controlDisabled = 'opacity-60 cursor-not-allowed bg-muted pointer-events-none shadow-none'

/** Floating panel used by every dropdown / popover surface. */
export const floatingPanel =
  'rounded-xl border border-border-default bg-white dark:bg-slate-900 text-primary shadow-lg ' +
  'shadow-slate-900/10 dark:shadow-black/50 outline-none animate-in fade-in-0 zoom-in-95'

/** Option rows inside listboxes and menus. */
export const optionRow =
  'relative flex w-full cursor-pointer select-none items-center gap-2 rounded-md px-2.5 py-2 text-sm outline-none transition-colors'
