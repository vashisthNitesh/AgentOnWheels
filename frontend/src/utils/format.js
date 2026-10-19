import { auth } from '../api'

const getTz = () => auth.user?.display_tz || 'Asia/Dubai'

export const tzLabel = () => getTz().split('/').pop().replace('_', ' ') + ' time'

/**
 * Format currency amount with symbol and fixed 2 decimals.
 */
export function formatCurrency(value, currency = 'AED', locale = 'en-US') {
  if (value === null || value === undefined || value === '') return '—'
  const n = Number(value)
  if (isNaN(n)) return '—'

  try {
    return new Intl.NumberFormat(locale, {
      style: currency && currency !== 'MIXED' ? 'currency' : 'decimal',
      currency: currency && currency !== 'MIXED' ? currency : undefined,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(n)
  } catch {
    return (currency ? currency + ' ' : '') + n.toFixed(2)
  }
}

/**
 * Format integer or decimal numbers with thousand separators.
 */
export function formatNumber(value, maxDecimals = 2, locale = 'en-US') {
  if (value === null || value === undefined || value === '') return '—'
  const n = Number(value)
  if (isNaN(n)) return '—'
  return new Intl.NumberFormat(locale, {
    maximumFractionDigits: maxDecimals,
  }).format(n)
}

/**
 * Format compact numbers (e.g. 1.2M, 45K)
 */
export function compact(value, currency = '') {
  if (value === null || value === undefined || value === '') return '—'
  const n = Number(value)
  if (isNaN(n)) return '—'
  const formatted = Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
  return currency && currency !== 'MIXED' ? `${currency} ${formatted}` : formatted
}

/**
 * Format weights in tonnes (t). Shows kg if specified in tooltip or converted.
 */
export function formatWeight(valueInTonnes, unit = 't') {
  if (valueInTonnes === null || valueInTonnes === undefined || valueInTonnes === '') return '—'
  const n = Number(valueInTonnes)
  if (isNaN(n)) return '—'
  return `${formatNumber(n, 2)} ${unit}`
}

/**
 * Format distance in kilometers (km).
 */
export function formatDistance(valueInKm) {
  if (valueInKm === null || valueInKm === undefined || valueInKm === '') return '—'
  const n = Number(valueInKm)
  if (isNaN(n)) return '—'
  return `${formatNumber(n, 0)} km`
}

/**
 * Format duration in minutes or hours to 'Xh Ym'.
 */
export function formatDuration(minutes) {
  if (minutes === null || minutes === undefined || minutes === '') return '—'
  const m = Number(minutes)
  if (isNaN(m) || m < 0) return '—'
  const hrs = Math.floor(m / 60)
  const rem = m % 60
  if (hrs === 0) return `${rem}m`
  if (rem === 0) return `${hrs}h`
  return `${hrs}h ${rem}m`
}

/**
 * Format date string (e.g. 2026-10-19)
 */
export function formatDate(value, locale = 'en-GB') {
  if (!value) return '—'
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [y, m, d] = value.split('-')
    return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString(locale, {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      timeZone: 'UTC',
    })
  }
  return new Date(value).toLocaleDateString(locale, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    timeZone: getTz(),
  })
}

/**
 * Format date and time
 */
export function formatDateTime(value, locale = 'en-GB') {
  if (!value) return '—'
  return new Date(value).toLocaleString(locale, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: getTz(),
  })
}

/**
 * Relative time formatter ("3 hours ago", "in 2 days")
 */
export function formatRelative(date) {
  if (!date) return '—'
  const d = new Date(date)
  if (isNaN(d.getTime())) return '—'
  const diffSec = Math.round((d.getTime() - Date.now()) / 1000)
  const absSec = Math.abs(diffSec)

  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  if (absSec < 60) return rtf.format(diffSec, 'second')
  if (absSec < 3600) return rtf.format(Math.round(diffSec / 60), 'minute')
  if (absSec < 86400) return rtf.format(Math.round(diffSec / 3600), 'hour')
  if (absSec < 2592000) return rtf.format(Math.round(diffSec / 86400), 'day')
  return formatDate(date)
}

/**
 * Format percentages.
 */
export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined || value === '') return '—'
  const n = Number(value)
  if (isNaN(n)) return '—'
  return `${n.toFixed(decimals)}%`
}

// ------------------------------------------------------------- Backward compatibility aliases
export const fmtDate = (v) => formatDate(v)
export const fmtMoney = (v, cur = '') => formatCurrency(v, cur)

export const STATUS_COLORS = {
  pending: 'bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-300',
  confirmed: 'bg-sky-100 text-sky-800 dark:bg-sky-950/40 dark:text-sky-300',
  active: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300',
  in_progress: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300',
  completed: 'bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-200',
  closed: 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  ready_for_invoice: 'bg-violet-100 text-violet-800 dark:bg-violet-950/40 dark:text-violet-300',
  invoiced: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/40 dark:text-indigo-300',
  cancelled: 'bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300',
  rejected: 'bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300',
  expired: 'bg-rose-50 text-rose-600 dark:bg-rose-950/40 dark:text-rose-400',
  unassigned: 'bg-orange-100 text-orange-800 dark:bg-orange-950/40 dark:text-orange-300',
  assigned: 'bg-sky-100 text-sky-800 dark:bg-sky-950/40 dark:text-sky-300',
  draft: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  sent: 'bg-sky-100 text-sky-800 dark:bg-sky-950/40 dark:text-sky-300',
  paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300',
  maintenance: 'bg-orange-100 text-orange-800 dark:bg-orange-950/40 dark:text-orange-300',
  inactive: 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400',
  created: 'bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-300',
  on_lease: 'bg-violet-100 text-violet-800 dark:bg-violet-950/40 dark:text-violet-300',
}
