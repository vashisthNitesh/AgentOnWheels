<template>
  <PopoverRoot v-model:open="isOpen">
    <PopoverTrigger as-child>
      <button
        type="button"
        v-bind="restAttrs"
        :disabled="disabled"
        aria-haspopup="dialog"
        :aria-expanded="isOpen"
        :class="cn(
          controlBase,
          'flex items-center gap-2 text-left select-none cursor-pointer',
          controlSizes[size],
          invalid ? controlInvalid : (isOpen ? controlOpen : controlIdle),
          disabled && controlDisabled,
          $attrs.class
        )"
      >
        <CalendarRange class="h-4 w-4 shrink-0 text-muted" />
        <span class="min-w-0 flex-1 truncate">
          <span v-if="displayRange" class="text-primary">{{ displayRange }}</span>
          <span v-else class="text-muted">{{ placeholder }}</span>
        </span>
        <span
          v-if="clearable && (start || end) && !disabled"
          role="button"
          tabindex="-1"
          class="shrink-0 rounded p-0.5 text-muted transition hover:bg-subtle hover:text-primary"
          aria-label="Clear range"
          @click.stop.prevent="clearRange"
        >
          <X class="h-3.5 w-3.5" />
        </span>
      </button>
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        align="start"
        :side-offset="6"
        :collision-padding="12"
        :class="cn(floatingPanel, 'z-dropdown flex max-w-[calc(100vw-24px)] flex-col gap-3 p-3 select-none sm:flex-row')"
      >
        <!-- Presets -->
        <div class="flex shrink-0 gap-1 overflow-x-auto border-b border-border-default pb-3 scrollbar-none sm:w-36 sm:flex-col sm:border-b-0 sm:border-r sm:pb-0 sm:pr-3">
          <button
            v-for="p in presets"
            :key="p.label"
            type="button"
            :class="cn(
              'whitespace-nowrap rounded-md px-2.5 py-1.5 text-left text-xs font-medium transition-colors',
              activePreset === p.label
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300'
                : 'text-secondary hover:bg-subtle hover:text-primary'
            )"
            @click="applyPreset(p)"
          >
            {{ p.label }}
          </button>
        </div>

        <!-- Calendar -->
        <div class="w-[264px]">
          <div class="mb-2 flex items-center justify-between">
            <button type="button" class="nav-btn" aria-label="Previous month" @click="viewMonth = subMonths(viewMonth, 1)">
              <ChevronLeft class="h-4 w-4" />
            </button>
            <span class="text-sm font-semibold text-primary">{{ format(viewMonth, 'MMMM yyyy') }}</span>
            <button type="button" class="nav-btn" aria-label="Next month" @click="viewMonth = addMonths(viewMonth, 1)">
              <ChevronRight class="h-4 w-4" />
            </button>
          </div>

          <div class="mb-1 grid grid-cols-7 text-center">
            <span v-for="d in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']" :key="d" class="py-1 text-[11px] font-medium text-muted">
              {{ d }}
            </span>
          </div>

          <div class="grid grid-cols-7 gap-y-0.5">
            <div
              v-for="day in calendarDays"
              :key="day.key"
              :class="cn(
                'flex h-9 items-center justify-center',
                day.isInRange && 'bg-primary-50 dark:bg-primary-950',
                day.isStart && day.hasEnd && 'rounded-l-lg bg-primary-50 dark:bg-primary-950',
                day.isEnd && 'rounded-r-lg bg-primary-50 dark:bg-primary-950'
              )"
              @mouseenter="hoverDate = day.date"
            >
              <button
                type="button"
                :class="cn(
                  'flex h-9 w-9 items-center justify-center rounded-lg text-sm tabular-nums transition-colors',
                  day.isCurrentMonth ? 'text-primary' : 'text-muted/50',
                  (day.isStart || day.isEnd)
                    ? 'bg-primary-600 font-semibold text-white dark:bg-primary-500'
                    : 'hover:bg-subtle',
                  day.isToday && !day.isStart && !day.isEnd && 'font-semibold text-primary-600 dark:text-primary-400'
                )"
                @click="selectDate(day.date)"
              >
                {{ day.date.getDate() }}
              </button>
            </div>
          </div>

          <div class="mt-3 flex items-center justify-between border-t border-border-default pt-2.5">
            <span class="text-[11px] text-muted">
              {{ tempStart ? formatDate(tempStart) : 'Start' }} → {{ tempEnd ? formatDate(tempEnd) : 'End' }}
            </span>
            <div class="flex items-center gap-2">
              <button type="button" class="text-xs text-secondary hover:text-primary" @click="isOpen = false">
                Cancel
              </button>
              <button
                type="button"
                class="rounded-md bg-primary-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40 dark:bg-primary-500"
                :disabled="!tempStart"
                @click="applyRange"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>

<script setup>
import { ref, computed, watch, useAttrs } from 'vue'
import { PopoverRoot, PopoverTrigger, PopoverPortal, PopoverContent } from 'reka-ui'
import { CalendarRange, ChevronLeft, ChevronRight, X } from 'lucide-vue-next'
import {
  format, subDays, startOfMonth, endOfMonth, startOfYear, subMonths, startOfQuarter, endOfQuarter,
  addMonths, isSameDay, isSameMonth,
} from 'date-fns'
import { cn } from '../../utils/cn'
import { formatDate } from '../../utils/format'
import {
  controlBase, controlSizes, controlIdle, controlOpen, controlInvalid, controlDisabled, floatingPanel,
} from './controlStyles'

defineOptions({ inheritAttrs: false })

/**
 * Supports two binding styles:
 *   v-model:start-value / v-model:end-value   (strings)
 *   v-model  → { from, to }                     (object, used by the filter drawer)
 */
const props = defineProps({
  startValue: { type: String, default: undefined },
  endValue: { type: String, default: undefined },
  modelValue: { type: Object, default: undefined },
  placeholder: { type: String, default: 'Select date range…' },
  size: { type: String, default: 'md' },
  disabled: { type: Boolean, default: false },
  invalid: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
})

const emit = defineEmits(['update:startValue', 'update:endValue', 'update:modelValue', 'change', 'clear'])

const attrs = useAttrs()
const restAttrs = computed(() => {
  const { class: _c, ...rest } = attrs
  return rest
})

const start = computed(() => props.modelValue?.from ?? props.startValue ?? '')
const end = computed(() => props.modelValue?.to ?? props.endValue ?? '')

const isOpen = ref(false)
const viewMonth = ref(startOfMonth(new Date()))
const tempStart = ref('')
const tempEnd = ref('')
const hoverDate = ref(null)
const activePreset = ref('')

const parseLocal = (s) => {
  if (!s) return null
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s)
  return m ? new Date(+m[1], +m[2] - 1, +m[3]) : new Date(s)
}

const toIsoDate = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

const displayRange = computed(() => {
  if (start.value && end.value) return `${formatDate(start.value)} – ${formatDate(end.value)}`
  if (start.value) return `From ${formatDate(start.value)}`
  if (end.value) return `Until ${formatDate(end.value)}`
  return ''
})

const presets = [
  { label: 'Today', getRange: () => [new Date(), new Date()] },
  { label: 'Yesterday', getRange: () => [subDays(new Date(), 1), subDays(new Date(), 1)] },
  { label: 'Last 7 days', getRange: () => [subDays(new Date(), 6), new Date()] },
  { label: 'Last 30 days', getRange: () => [subDays(new Date(), 29), new Date()] },
  { label: 'This month', getRange: () => [startOfMonth(new Date()), endOfMonth(new Date())] },
  { label: 'Last month', getRange: () => [startOfMonth(subMonths(new Date(), 1)), endOfMonth(subMonths(new Date(), 1))] },
  { label: 'This quarter', getRange: () => [startOfQuarter(new Date()), endOfQuarter(new Date())] },
  { label: 'Year to date', getRange: () => [startOfYear(new Date()), new Date()] },
]

watch(isOpen, (open) => {
  if (!open) return
  tempStart.value = start.value || ''
  tempEnd.value = end.value || ''
  viewMonth.value = startOfMonth(parseLocal(start.value) || new Date())
  activePreset.value = ''
})

const calendarDays = computed(() => {
  const mStart = startOfMonth(viewMonth.value)
  const offset = (mStart.getDay() + 6) % 7
  const first = new Date(mStart)
  first.setDate(first.getDate() - offset)
  const s = parseLocal(tempStart.value)
  // While picking the end date, preview the range under the cursor.
  const e = parseLocal(tempEnd.value) || (s && hoverDate.value && hoverDate.value > s ? hoverDate.value : null)
  const today = new Date()
  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(first)
    d.setDate(first.getDate() + i)
    const isStart = s ? isSameDay(d, s) : false
    const isEnd = e ? isSameDay(d, e) : false
    return {
      key: d.toDateString(),
      date: d,
      isCurrentMonth: isSameMonth(d, viewMonth.value),
      isToday: isSameDay(d, today),
      isStart,
      isEnd,
      hasEnd: !!e && !isSameDay(s, e),
      isInRange: !!(s && e && d > s && d < e),
    }
  })
})

function selectDate(d) {
  activePreset.value = ''
  const iso = toIsoDate(d)
  if (!tempStart.value || tempEnd.value) {
    tempStart.value = iso
    tempEnd.value = ''
  } else if (parseLocal(iso) < parseLocal(tempStart.value)) {
    tempEnd.value = tempStart.value
    tempStart.value = iso
  } else {
    tempEnd.value = iso
  }
}

function emitRange(from, to) {
  emit('update:startValue', from)
  emit('update:endValue', to)
  emit('update:modelValue', from || to ? { from, to } : null)
  emit('change', { start: from, end: to })
}

function applyPreset(p) {
  activePreset.value = p.label
  const [s, e] = p.getRange()
  tempStart.value = toIsoDate(s)
  tempEnd.value = toIsoDate(e)
  applyRange()
}

function applyRange() {
  if (!tempStart.value) return
  emitRange(tempStart.value, tempEnd.value || tempStart.value)
  isOpen.value = false
}

function clearRange() {
  emitRange('', '')
  emit('clear')
}
</script>

<style scoped>
.nav-btn {
  @apply inline-flex h-7 w-7 items-center justify-center rounded-md text-secondary transition hover:bg-subtle hover:text-primary;
}
</style>
