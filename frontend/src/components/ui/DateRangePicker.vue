<template>
  <div ref="containerRef" class="relative w-full">
    <!-- Trigger Input Box -->
    <div
      tabindex="0"
      :class="cn(
        'w-full flex items-center justify-between bg-surface text-primary border rounded-md transition text-left focus-ring select-none cursor-pointer',
        sizeClasses,
        invalid ? 'border-danger-500 focus:border-danger-500 ring-2 ring-danger-500/20' : 'border-border-strong hover:border-slate-400 dark:hover:border-slate-500 focus:border-primary-500',
        disabled && 'opacity-60 cursor-not-allowed bg-muted pointer-events-none',
        $attrs.class
      )"
      @click="toggleOpen"
      @keydown.esc="close"
    >
      <div class="flex items-center gap-2 truncate flex-1">
        <CalendarIcon class="w-4 h-4 text-secondary shrink-0" />
        <span v-if="displayRange" class="truncate font-medium text-xs">{{ displayRange }}</span>
        <span v-else class="text-muted text-xs truncate">{{ placeholder || 'Select date range…' }}</span>
      </div>

      <div class="flex items-center gap-1 ml-2 shrink-0">
        <button
          v-if="clearable && (startValue || endValue) && !disabled"
          type="button"
          tabindex="-1"
          class="text-secondary hover:text-primary p-0.5 rounded transition"
          aria-label="Clear range"
          @click.stop="clearRange"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

    <!-- Dropdown Modal with Presets Rail and Dual Calendars -->
    <div
      v-if="isOpen"
      class="absolute left-0 top-full mt-1 z-dropdown rounded-xl border border-border-default bg-surface-raised text-primary shadow-xl p-4 select-none animate-in fade-in zoom-in-95 duration-150 flex flex-col md:flex-row gap-4"
    >
      <!-- Left Rail: Presets -->
      <div class="flex md:flex-col gap-1 border-b md:border-b-0 md:border-r border-border-default pb-3 md:pb-0 md:pr-4 overflow-x-auto shrink-0 min-w-[130px]">
        <button
          v-for="p in presets"
          :key="p.label"
          type="button"
          :class="cn(
            'px-2.5 py-1.5 rounded-md text-xs font-medium text-left transition-colors whitespace-nowrap focus-ring',
            activePreset === p.label ? 'bg-primary-50 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300 font-semibold' : 'hover:bg-subtle text-secondary'
          )"
          @click="applyPreset(p)"
        >
          {{ p.label }}
        </button>
      </div>

      <!-- Calendar View -->
      <div class="flex flex-col gap-3">
        <!-- Dual Month Controls -->
        <div class="flex items-center justify-between pb-2 border-b border-border-default">
          <button
            type="button"
            class="p-1 rounded text-secondary hover:text-primary hover:bg-subtle transition focus-ring"
            @click="prevMonth"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>

          <span class="text-xs font-semibold text-primary">
            {{ format(viewMonth, 'MMMM yyyy') }}
          </span>

          <button
            type="button"
            class="p-1 rounded text-secondary hover:text-primary hover:bg-subtle transition focus-ring"
            @click="nextMonth"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>

        <!-- Days Grid -->
        <div class="grid grid-cols-7 gap-1 text-center mb-1">
          <span v-for="d in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']" :key="d" class="text-[10px] font-semibold text-muted py-0.5">
            {{ d }}
          </span>
        </div>

        <div class="grid grid-cols-7 gap-1 text-center">
          <button
            v-for="(day, idx) in calendarDays"
            :key="idx"
            type="button"
            :class="cn(
              'w-7 h-7 rounded text-xs flex items-center justify-center font-medium transition-colors focus-ring',
              day.isCurrentMonth ? 'text-primary' : 'text-muted/50',
              (day.isStart || day.isEnd) && 'bg-primary-600 text-white font-semibold shadow-xs dark:bg-primary-500',
              day.isInRange && !day.isStart && !day.isEnd && 'bg-primary-50 dark:bg-primary-950/40 text-primary-700 dark:text-primary-300 rounded-none',
              day.isToday && !day.isStart && !day.isEnd && 'border border-primary-500 font-semibold'
            )"
            @click="selectDate(day.date)"
          >
            {{ day.date.getDate() }}
          </button>
        </div>

        <!-- Footer Actions -->
        <div class="mt-2 pt-2 border-t border-border-default flex items-center justify-between text-xs">
          <span class="text-muted text-[11px] font-mono">
            {{ tempStart ? formatDate(tempStart) : 'Start' }} → {{ tempEnd ? formatDate(tempEnd) : 'End' }}
          </span>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="px-2.5 py-1 text-xs text-secondary hover:text-primary"
              @click="close"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn-primary !h-7 !px-3 !text-xs"
              :disabled="!tempStart || !tempEnd"
              @click="applyRange"
            >
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, X } from 'lucide-vue-next'
import { onClickOutside } from '@vueuse/core'
import {
  format,
  subDays,
  startOfMonth,
  endOfMonth,
  startOfYear,
  subMonths,
  startOfQuarter,
  endOfQuarter,
  addMonths,
  isSameDay,
  isSameMonth,
  isAfter,
  isBefore,
} from 'date-fns'
import { cn } from '../../utils/cn'
import { formatDate } from '../../utils/format'

const props = defineProps({
  startValue: {
    type: String,
    default: '',
  },
  endValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Filter by date range…',
  },
  size: {
    type: String,
    default: 'md',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  invalid: {
    type: Boolean,
    default: false,
  },
  clearable: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:startValue', 'update:endValue', 'change', 'clear'])

const containerRef = ref(null)
const isOpen = ref(false)
const viewMonth = ref(new Date())

const tempStart = ref(props.startValue || '')
const tempEnd = ref(props.endValue || '')
const activePreset = ref('')

onClickOutside(containerRef, () => {
  if (isOpen.value) close()
})

const sizeClasses = computed(() => {
  return {
    sm: 'h-8 px-2.5',
    md: 'h-9 px-3',
    lg: 'h-10 px-3.5',
  }[props.size]
})

const displayRange = computed(() => {
  if (props.startValue && props.endValue) {
    return `${formatDate(props.startValue)} – ${formatDate(props.endValue)}`
  }
  if (props.startValue) return `From ${formatDate(props.startValue)}`
  return ''
})

const toIsoDate = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dt = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dt}`
}

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

function applyPreset(p) {
  activePreset.value = p.label
  const [s, e] = p.getRange()
  tempStart.value = toIsoDate(s)
  tempEnd.value = toIsoDate(e)
  applyRange()
}

const calendarDays = computed(() => {
  const mStart = startOfMonth(viewMonth.value)
  const startDay = (mStart.getDay() + 6) % 7
  const prevMonthDate = new Date(mStart)
  prevMonthDate.setDate(prevMonthDate.getDate() - startDay)

  const days = []
  const sDate = tempStart.value ? new Date(tempStart.value) : null
  const eDate = tempEnd.value ? new Date(tempEnd.value) : null

  for (let i = 0; i < 42; i++) {
    const d = new Date(prevMonthDate)
    d.setDate(prevMonthDate.getDate() + i)

    const isStart = sDate ? isSameDay(d, sDate) : false
    const isEnd = eDate ? isSameDay(d, eDate) : false
    const isInRange = sDate && eDate && isAfter(d, sDate) && isBefore(d, eDate)

    days.push({
      date: d,
      isCurrentMonth: isSameMonth(d, viewMonth.value),
      isToday: isSameDay(d, new Date()),
      isStart,
      isEnd,
      isInRange,
    })
  }

  return days
})

function selectDate(d) {
  activePreset.value = 'Custom'
  const iso = toIsoDate(d)
  if (!tempStart.value || (tempStart.value && tempEnd.value)) {
    tempStart.value = iso
    tempEnd.value = ''
  } else if (tempStart.value && !tempEnd.value) {
    if (new Date(iso) < new Date(tempStart.value)) {
      tempEnd.value = tempStart.value
      tempStart.value = iso
    } else {
      tempEnd.value = iso
    }
  }
}

function applyRange() {
  if (tempStart.value && tempEnd.value) {
    emit('update:startValue', tempStart.value)
    emit('update:endValue', tempEnd.value)
    emit('change', { start: tempStart.value, end: tempEnd.value })
    close()
  }
}

function clearRange() {
  tempStart.value = ''
  tempEnd.value = ''
  activePreset.value = ''
  emit('update:startValue', '')
  emit('update:endValue', '')
  emit('clear')
}

function prevMonth() {
  viewMonth.value = subMonths(viewMonth.value, 1)
}

function nextMonth() {
  viewMonth.value = addMonths(viewMonth.value, 1)
}

function toggleOpen() {
  if (isOpen.value) close()
  else {
    tempStart.value = props.startValue || ''
    tempEnd.value = props.endValue || ''
    isOpen.value = true
  }
}

function close() {
  isOpen.value = false
}
</script>
