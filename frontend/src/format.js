import { auth } from './api'
const tz = () => auth.user?.display_tz || 'Asia/Dubai'
export const tzLabel = () => tz().split('/').pop().replace('_', ' ') + ' time'
export function fmtDate(v) {
  if (!v) return '—'
  if (/^\d{4}-\d{2}-\d{2}$/.test(v)) { const [y, m, d] = v.split('-'); return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' }) }
  return new Date(v).toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: tz() })
}
export function fmtMoney(v, cur = '') {
  if (v === null || v === undefined || v === '') return '—'
  const n = Number(v)
  return (cur ? cur + ' ' : '') + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
export function compact(v, cur = '') {
  if (v === null || v === undefined) return '—'
  return (cur && cur !== 'MIXED' ? cur + ' ' : '') + Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(v)
}
export const STATUS_COLORS = {
  pending: 'bg-amber-100 text-amber-800', confirmed: 'bg-sky-100 text-sky-800', active: 'bg-emerald-100 text-emerald-800', in_progress: 'bg-emerald-100 text-emerald-800',
  completed: 'bg-slate-200 text-slate-800', closed: 'bg-slate-200 text-slate-700', ready_for_invoice: 'bg-violet-100 text-violet-800', invoiced: 'bg-indigo-100 text-indigo-800',
  cancelled: 'bg-rose-100 text-rose-700', rejected: 'bg-rose-100 text-rose-700', expired: 'bg-rose-50 text-rose-600', unassigned: 'bg-orange-100 text-orange-800',
  assigned: 'bg-sky-100 text-sky-800', draft: 'bg-slate-100 text-slate-700', sent: 'bg-sky-100 text-sky-800', paid: 'bg-emerald-100 text-emerald-800',
  maintenance: 'bg-orange-100 text-orange-800', inactive: 'bg-slate-100 text-slate-500', created: 'bg-amber-100 text-amber-800', on_lease: 'bg-violet-100 text-violet-800',
}
