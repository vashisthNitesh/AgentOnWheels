<template>
  <span
    :class="cn(
      'inline-flex items-center gap-1.5 font-medium rounded-full border transition-colors select-none',
      size === 'sm' ? 'text-xs px-2.5 py-0.5' : 'text-sm px-3 py-1',
      toneStyles.bg,
      toneStyles.text,
      toneStyles.border,
      $attrs.class
    )"
  >
    <!-- Indicator Dot with optional Pulse for live in-transit statuses -->
    <span class="relative flex h-2 w-2 shrink-0">
      <span
        v-if="meta.pulse"
        :class="cn('animate-ping motion-reduce:animate-none absolute inline-flex h-full w-full rounded-full opacity-75', toneStyles.dot)"
      />
      <span :class="cn('relative inline-flex rounded-full h-2 w-2', toneStyles.dot)" />
    </span>

    <!-- Optional Icon -->
    <component
      :is="iconComponent"
      v-if="showIcon && iconComponent"
      class="w-3.5 h-3.5 shrink-0 opacity-80"
    />

    <!-- Status Label -->
    <span class="truncate">{{ label || meta.label }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import {
  CheckCircle2, CheckCheck, PackageCheck, BadgeCheck, Check, ThumbsUp, Sparkles, History,
  PlayCircle, Truck, Navigation, Cog,
  ShieldCheck, UserCheck, Calendar, Receipt, FileText, Send, Search, FilePlus, BarChart3,
  CheckSquare, Clock, Clock4, FileEdit, PlusCircle, HelpCircle, FolderOpen, FolderCheck, MinusCircle,
  AlertTriangle, PauseCircle, Wrench, Key, AlertCircle, ClockAlert,
  XCircle, Ban, AlertOctagon, FileX
} from 'lucide-vue-next'
import { getStatusMeta, TONE_STYLES } from '../../design/status'
import { cn } from '../../utils/cn'

const ICON_MAP = {
  CheckCircle2, CheckCheck, PackageCheck, BadgeCheck, Check, ThumbsUp, Sparkles, History,
  PlayCircle, Truck, Navigation, Cog,
  ShieldCheck, UserCheck, Calendar, Receipt, FileText, Send, Search, FilePlus, BarChart3,
  CheckSquare, Clock, Clock4, FileEdit, PlusCircle, HelpCircle, FolderOpen, FolderCheck, MinusCircle,
  AlertTriangle, PauseCircle, Wrench, Key, AlertCircle, ClockAlert,
  XCircle, Ban, AlertOctagon, FileX
}

const props = defineProps({
  status: {
    type: [String, Number],
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: 'sm',
    validator: v => ['sm', 'md'].includes(v),
  },
  showIcon: {
    type: Boolean,
    default: true,
  },
})

const meta = computed(() => getStatusMeta(props.status, props.label))
const toneStyles = computed(() => TONE_STYLES[meta.value.tone] || TONE_STYLES.neutral)

const iconComponent = computed(() => {
  if (!meta.value.icon) return null
  return ICON_MAP[meta.value.icon] || HelpCircle
})
</script>
