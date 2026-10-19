<template>
  <div ref="containerRef" :class="cn('relative w-full', isOpen && 'z-50')">
    <!-- Trigger Input Box -->
    <div
      :id="triggerId"
      tabindex="0"
      :aria-haspopup="'dialog'"
      :aria-expanded="isOpen"
      :class="cn(
        'w-full flex items-center justify-between bg-surface text-primary border rounded-md transition text-left focus-ring select-none cursor-pointer',
        sizeClasses,
        (invalid || fieldCtx?.invalid?.value)
          ? 'border-danger-500 focus:border-danger-500 ring-2 ring-danger-500/20'
          : 'border-border-strong hover:border-slate-400 dark:hover:border-slate-500 focus:border-primary-500',
        disabled && 'opacity-60 cursor-not-allowed bg-muted pointer-events-none',
        $attrs.class
      )"
      @click="toggleOpen"
      @keydown.esc="close"
    >
      <div class="flex items-center gap-2 truncate flex-1">
        <CalendarIcon class="w-4 h-4 text-secondary shrink-0" />
        <span v-if="displayValue" class="truncate font-medium">{{ displayValue }}</span>
        <span v-else class="text-muted font-normal truncate">{{ placeholder || (withTime ? 'Select date & time…' : 'Select date…') }}</span>
      </div>

      <div class="flex items-center gap-1 ml-2 shrink-0">
        <button
          v-if="clearable && modelValue && !disabled"
          type="button"
          tabindex="-1"
          class="text-secondary hover:text-primary p-0.5 rounded transition"
          aria-label="Clear date"
          @click.stop="clearDate"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

    <!-- Calendar Popover -->
    <div
      v-if="isOpen"
      :class="cn(
        'absolute left-0 z-dropdown rounded-lg border border-border-default bg-surface-raised bg-white dark:bg-slate-900 text-primary shadow-xl shadow-slate-950/15 dark:shadow-black/60 p-3.5 select-none animate-in fade-in zoom-in-95 duration-150',
        openUpward ? 'bottom-full mb-1' : 'top-full mt-1'
      )"
    >
      <!-- Month & Year Navigation -->
      <div class="flex items-center justify-between mb-3 pb-2 border-b border-border-default">
        <button
          type="button"
          class="p-1 rounded text-secondary hover:text-primary hover:bg-subtle transition focus-ring"
          title="Previous month"
          @click="prevMonth"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>

        <span class="text-xs font-semibold text-primary">
          {{ currentMonthLabel }}
        </span>

        <button
          type="button"
          class="p-1 rounded text-secondary hover:text-primary hover:bg-subtle transition focus-ring"
          title="Next month"
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
          :disabled="day.disabled"
          :class="cn(
            'w-7 h-7 rounded text-xs flex items-center justify-center font-medium transition-colors focus-ring',
            day.isCurrentMonth ? 'text-primary' : 'text-muted/50',
            day.isSelected
              ? 'bg-primary-600 text-white font-semibold shadow-xs dark:bg-primary-500'
              : 'hover:bg-subtle',
            day.isToday && !day.isSelected && 'border border-primary-500 font-semibold text-primary-600 dark:text-primary-400'
          )"
          @click="selectDay(day)"
        >
          {{ day.date.getDate() }}
        </button>
      </div>

      <!-- Time Selector (if withTime is true) -->
      <div v-if="withTime" class="mt-3 pt-3 border-t border-border-default flex items-center justify-between text-xs">
        <span class="text-secondary flex items-center gap-1 font-medium">
          <Clock class="w-3.5 h-3.5" /> Time
        </span>
        <div class="flex items-center gap-1">
          <select v-model="selectedHour" class="h-6 rounded border border-border-strong bg-surface px-1 text-xs focus-ring">
            <option v-for="h in 24" :key="h-1" :value="String(h-1).padStart(2, '0')">{{ String(h-1).padStart(2, '0') }}</option>
          </select>
          <span>:</span>
          <select v-model="selectedMinute" class="h-6 rounded border border-border-strong bg-surface px-1 text-xs focus-ring">
            <option v-for="m in ['00', '15', '30', '45']" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
      </div>

      <!-- Quick Action: Today -->
      <div class="mt-3 pt-2 border-t border-border-default flex items-center justify-between text-xs">
        <button
          type="button"
          class="text-primary-600 dark:text-primary-400 font-medium hover:underline text-[11px]"
          @click="selectToday"
        >
          Today
        </button>
        <button
          type="button"
          class="text-secondary hover:text-primary text-[11px]"
          @click="close"
        >
          Done
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, inject } from 'vue'
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, X, Clock } from 'lucide-vue-next'
import { onClickOutside } from '@vueuse/core'
import { format, parseISO, isValid, startOfMonth, endOfMonth, addMonths, subMonths, isSameDay, isSameMonth } from 'date-fns'
import { cn } from '../../utils/cn'
import { formatDate, formatDateTime } from '../../utils/format'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  withTime: {
    type: Boolean,
    default: false,
  },
  placeholder: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg'].includes(v),
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
  id: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'change', 'clear'])

const fieldCtx = inject('formField', null)
const triggerId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)

const containerRef = ref(null)
const isOpen = ref(false)

const viewDate = ref(new Date())
const selectedHour = ref('12')
const selectedMinute = ref('00')

onClickOutside(containerRef, () => {
  if (isOpen.value) close()
})

const sizeClasses = computed(() => {
  return {
    sm: 'h-8 text-xs px-2.5',
    md: 'h-9 text-sm px-3',
    lg: 'h-10 text-base px-3.5',
  }[props.size]
})

const parsedDate = computed(() => {
  if (!props.modelValue) return null
  const d = new Date(props.modelValue)
  return isValid(d) ? d : null
})

const displayValue = computed(() => {
  if (!parsedDate.value) return ''
  return props.withTime ? formatDateTime(props.modelValue) : formatDate(props.modelValue)
})

const currentMonthLabel = computed(() => {
  return format(viewDate.value, 'MMMM yyyy')
})

const calendarDays = computed(() => {
  const monthStart = startOfMonth(viewDate.value)
  const monthEnd = endOfMonth(viewDate.value)

  // Start on Monday (ISO 8601)
  const startDay = (monthStart.getDay() + 6) % 7
  const days = []

  // Fill preceding days from previous month
  const prevMonthDate = new Date(monthStart)
  prevMonthDate.setDate(prevMonthDate.getDate() - startDay)

  for (let i = 0; i < 42; i++) {
    const d = new Date(prevMonthDate)
    d.setDate(prevMonthDate.getDate() + i)
    days.push({
      date: d,
      isCurrentMonth: isSameMonth(d, viewDate.value),
      isToday: isSameDay(d, new Date()),
      isSelected: parsedDate.value ? isSameDay(d, parsedDate.value) : false,
      disabled: false,
    })
  }

  return days
})

const openUpward = ref(false)

function checkPosition() {
  if (!containerRef.value || typeof window === 'undefined') return
  const rect = containerRef.value.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom
  openUpward.value = spaceBelow < 340 && rect.top > 340
}

function toggleOpen() {
  if (isOpen.value) close()
  else {
    checkPosition()
    if (parsedDate.value) {
      viewDate.value = new Date(parsedDate.value)
      selectedHour.value = String(parsedDate.value.getHours()).padStart(2, '0')
      selectedMinute.value = String(Math.floor(parsedDate.value.getMinutes() / 15) * 15).padStart(2, '0')
    }
    isOpen.value = true
  }
}

function close() {
  isOpen.value = false
}

function prevMonth() {
  viewDate.value = subMonths(viewDate.value, 1)
}

function nextMonth() {
  viewDate.value = addMonths(viewDate.value, 1)
}

function selectDay(day) {
  const d = new Date(day.date)
  if (props.withTime) {
    d.setHours(Number(selectedHour.value), Number(selectedMinute.value), 0, 0)
    emit('update:modelValue', d.toISOString())
  } else {
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const dt = String(d.getDate()).padStart(2, '0')
    emit('update:modelValue', `${y}-${m}-${dt}`)
    close()
  }
}

function selectToday() {
  const now = new Date()
  viewDate.value = now
  selectDay({ date: now })
}

function clearDate() {
  emit('update:modelValue', '')
  emit('clear')
}

watch([selectedHour, selectedMinute], () => {
  if (props.withTime && parsedDate.value && isOpen.value) {
    const d = new Date(parsedDate.value)
    d.setHours(Number(selectedHour.value), Number(selectedMinute.value), 0, 0)
    emit('update:modelValue', d.toISOString())
  }
})
</script>
