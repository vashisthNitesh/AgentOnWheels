/**
 * AgentOnWheels Status Vocabulary & Semantic Mapping
 * Covers all 38 backend status values + common runtime statuses.
 */

export const STATUS_MAP = {
  // Success Tone (delivered, completed, paid, active, accepted, approved, sourced)
  active: { key: 'active', label: 'Active', tone: 'success', icon: 'CheckCircle2' },
  completed: { key: 'completed', label: 'Completed', tone: 'success', icon: 'CheckCheck' },
  delivered: { key: 'delivered', label: 'Delivered', tone: 'success', icon: 'PackageCheck' },
  paid: { key: 'paid', label: 'Paid', tone: 'success', icon: 'BadgeCheck' },
  accepted: { key: 'accepted', label: 'Accepted', tone: 'success', icon: 'Check' },
  approved: { key: 'approved', label: 'Approved', tone: 'success', icon: 'ThumbsUp' },
  sourced: { key: 'sourced', label: 'Sourced', tone: 'success', icon: 'Sparkles' },
  used: { key: 'used', label: 'Used', tone: 'success', icon: 'History' },

  // Accent Tone (Live / in-motion / executing / pulse)
  in_progress: { key: 'in_progress', label: 'In progress', tone: 'accent', icon: 'PlayCircle', pulse: true },
  in_transit: { key: 'in_transit', label: 'In transit', tone: 'accent', icon: 'Truck', pulse: true },
  on_road: { key: 'on_road', label: 'On the road', tone: 'accent', icon: 'Navigation', pulse: true },
  in_use: { key: 'in_use', label: 'In use', tone: 'accent', icon: 'Cog' },

  // Info Tone (confirmed, allocated, scheduled, documents issued, invoiced)
  confirmed: { key: 'confirmed', label: 'Confirmed', tone: 'info', icon: 'ShieldCheck' },
  assigned: { key: 'assigned', label: 'Assigned', tone: 'info', icon: 'UserCheck' },
  scheduled: { key: 'scheduled', label: 'Scheduled', tone: 'info', icon: 'Calendar' },
  ready_for_invoice: { key: 'ready_for_invoice', label: 'Ready for invoice', tone: 'info', icon: 'Receipt' },
  invoiced: { key: 'invoiced', label: 'Invoiced', tone: 'info', icon: 'FileText' },
  issued: { key: 'issued', label: 'Issued', tone: 'info', icon: 'Send' },
  sent: { key: 'sent', label: 'Sent', tone: 'info', icon: 'Send' },
  sourcing: { key: 'sourcing', label: 'Sent to sourcing', tone: 'info', icon: 'Search' },
  bid_created: { key: 'bid_created', label: 'Bid created', tone: 'info', icon: 'FilePlus' },
  generated: { key: 'generated', label: 'Generated', tone: 'info', icon: 'BarChart3' },

  // Neutral Tone (draft, pending, available, open, closed)
  available: { key: 'available', label: 'Available', tone: 'neutral', icon: 'CheckSquare' },
  pending: { key: 'pending', label: 'Pending', tone: 'warning', icon: 'Clock' },
  pending_approval: { key: 'pending_approval', label: 'Pending approval', tone: 'warning', icon: 'Clock4' },
  draft: { key: 'draft', label: 'Draft', tone: 'neutral', icon: 'FileEdit' },
  created: { key: 'created', label: 'Created', tone: 'neutral', icon: 'PlusCircle' },
  requested: { key: 'requested', label: 'Requested', tone: 'neutral', icon: 'HelpCircle' },
  open: { key: 'open', label: 'Open', tone: 'neutral', icon: 'FolderOpen' },
  closed: { key: 'closed', label: 'Closed', tone: 'neutral', icon: 'FolderCheck' },
  inactive: { key: 'inactive', label: 'Inactive', tone: 'neutral', icon: 'MinusCircle' },

  // Warning Tone (delayed, needs truck, on hold, maintenance, lease, disputed)
  unassigned: { key: 'unassigned', label: 'Needs a truck', tone: 'warning', icon: 'AlertTriangle' },
  on_hold: { key: 'on_hold', label: 'On hold', tone: 'warning', icon: 'PauseCircle' },
  maintenance: { key: 'maintenance', label: 'In maintenance', tone: 'warning', icon: 'Wrench' },
  on_lease: { key: 'on_lease', label: 'On lease', tone: 'warning', icon: 'Key' },
  disputed: { key: 'disputed', label: 'Disputed', tone: 'warning', icon: 'AlertCircle' },
  delayed: { key: 'delayed', label: 'Delayed', tone: 'warning', icon: 'ClockAlert' },

  // Danger Tone (cancelled, rejected, expired, failed, overdue, void)
  cancelled: { key: 'cancelled', label: 'Cancelled', tone: 'danger', icon: 'XCircle' },
  rejected: { key: 'rejected', label: 'Rejected', tone: 'danger', icon: 'Ban' },
  expired: { key: 'expired', label: 'Expired', tone: 'danger', icon: 'ClockAlert' },
  failed: { key: 'failed', label: 'Failed', tone: 'danger', icon: 'AlertOctagon' },
  void: { key: 'void', label: 'Void', tone: 'danger', icon: 'FileX' },
}

/**
 * Tone styling configuration for StatusPills, badges, and kanban indicators
 */
export const TONE_STYLES = {
  success: {
    bg: 'bg-emerald-50 dark:bg-emerald-950/40',
    text: 'text-emerald-700 dark:text-emerald-300',
    border: 'border-emerald-200 dark:border-emerald-800',
    dot: 'bg-emerald-500',
  },
  accent: {
    bg: 'bg-accent-50 dark:bg-accent-950/40',
    text: 'text-accent-700 dark:text-accent-300',
    border: 'border-accent-200 dark:border-accent-800',
    dot: 'bg-accent-500',
  },
  info: {
    bg: 'bg-sky-50 dark:bg-sky-950/40',
    text: 'text-sky-700 dark:text-sky-300',
    border: 'border-sky-200 dark:border-sky-800',
    dot: 'bg-sky-500',
  },
  warning: {
    bg: 'bg-amber-50 dark:bg-amber-950/40',
    text: 'text-amber-800 dark:text-amber-300',
    border: 'border-amber-200 dark:border-amber-800',
    dot: 'bg-amber-500',
  },
  danger: {
    bg: 'bg-rose-50 dark:bg-rose-950/40',
    text: 'text-rose-700 dark:text-rose-300',
    border: 'border-rose-200 dark:border-rose-800',
    dot: 'bg-rose-500',
  },
  neutral: {
    bg: 'bg-slate-100 dark:bg-slate-800/80',
    text: 'text-slate-700 dark:text-slate-300',
    border: 'border-slate-200 dark:border-slate-700',
    dot: 'bg-slate-400',
  },
}

/**
 * Returns complete status descriptor with safe fallback for any unknown status.
 * @param {string|null|undefined} statusKey
 * @param {string} [fallbackLabel]
 * @returns {{ key: string, label: string, tone: 'success'|'accent'|'info'|'warning'|'danger'|'neutral', icon: string, pulse?: boolean }}
 */
export function getStatusMeta(statusKey, fallbackLabel = '') {
  if (!statusKey) {
    return { key: 'unknown', label: '—', tone: 'neutral', icon: 'HelpCircle' }
  }

  const s = String(statusKey).toLowerCase().trim()
  if (STATUS_MAP[s]) {
    return { ...STATUS_MAP[s], label: fallbackLabel || STATUS_MAP[s].label }
  }

  // Graceful fallback for custom or unmapped statuses
  const humanized = fallbackLabel || s.replace(/_/g, ' ').replace(/^./, str => str.toUpperCase())
  return {
    key: s,
    label: humanized,
    tone: 'neutral',
    icon: 'HelpCircle',
  }
}
