<template>
  <PopoverRoot v-model:open="isOpen">
    <PopoverTrigger as-child>
      <button
        :id="triggerId"
        type="button"
        v-bind="restAttrs"
        :disabled="disabled"
        aria-haspopup="dialog"
        :aria-expanded="isOpen"
        :aria-invalid="isInvalid || undefined"
        :aria-describedby="fieldCtx?.describedBy?.value"
        :class="cn(
          controlBase,
          'flex items-center gap-2 text-left select-none cursor-pointer',
          controlSizes[size],
          isInvalid ? controlInvalid : (isOpen ? controlOpen : controlIdle),
          disabled && controlDisabled,
          $attrs.class
        )"
      >
        <CalendarIcon class="h-4 w-4 shrink-0 text-muted" />
        <span class="min-w-0 flex-1 truncate">
          <span v-if="displayValue" class="text-primary">{{ displayValue }}</span>
          <span v-else class="text-muted">{{ placeholder || (timeEnabled ? 'Select date & time…' : 'Select date…') }}</span>
        </span>
        <span
          v-if="clearable && modelValue && !disabled"
          role="button"
          tabindex="-1"
          class="shrink-0 rounded p-0.5 text-muted transition hover:bg-subtle hover:text-primary"
          aria-label="Clear date"
          @click.stop.prevent="clearDate"
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
        :class="cn(floatingPanel, 'z-dropdown w-[288px] p-3 select-none')"
        @close-auto-focus="$emit('blur')"
      >
        <!-- Month navigation -->
        <div class="mb-2 flex items-center justify-between">
          <div class="flex items-center">
            <button type="button" class="nav-btn" title="Previous year" @click="shiftMonth(-12)">
              <ChevronsLeft class="h-4 w-4" />
            </button>
            <button type="button" class="nav-btn" title="Previous month" @click="shiftMonth(-1)">
              <ChevronLeft class="h-4 w-4" />
            </button>
          </div>
          <span class="text-sm font-semibold text-primary">{{ currentMonthLabel }}</span>
          <div class="flex items-center">
            <button type="button" class="nav-btn" title="Next month" @click="shiftMonth(1)">
              <ChevronRight class="h-4 w-4" />
            </button>
            <button type="button" class="nav-btn" title="Next year" @click="shiftMonth(12)">
              <ChevronsRight class="h-4 w-4" />
            </button>
          </div>
        </div>

        <!-- Weekday header -->
        <div class="mb-1 grid grid-cols-7 text-center">
          <span v-for="d in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']" :key="d" class="py-1 text-[11px] font-medium text-muted">
            {{ d }}
          </span>
        </div>

        <!-- Days -->
        <div class="grid grid-cols-7 gap-0.5" role="grid">
          <button
            v-for="day in calendarDays"
            :key="day.key"
            type="button"
            :disabled="day.disabled"
            :aria-pressed="day.isSelected"
            :aria-label="day.label"
            :class="cn(
              'mx-auto flex h-9 w-9 items-center justify-center rounded-lg text-sm tabular-nums transition-colors focus-ring',
              day.isCurrentMonth ? 'text-primary' : 'text-muted/50',
              day.isSelected
                ? 'bg-primary-600 font-semibold text-white shadow-xs hover:bg-primary-700 dark:bg-primary-500'
                : 'hover:bg-subtle',
              day.isToday && !day.isSelected && 'font-semibold text-primary-600 ring-1 ring-inset ring-primary-500/50 dark:text-primary-400',
              day.disabled && 'pointer-events-none opacity-30'
            )"
            @click="selectDay(day.date)"
          >
            {{ day.date.getDate() }}
          </button>
        </div>

        <!-- Time -->
        <div v-if="timeEnabled" class="mt-3 flex items-center justify-between gap-3 border-t border-border-default pt-3">
          <span class="flex items-center gap-1.5 text-xs font-medium text-secondary">
            <Clock class="h-3.5 w-3.5" /> Time
          </span>
          <input
            v-model="timeValue"
            type="time"
            step="300"
            class="h-8 rounded-md border border-border-strong bg-surface px-2 text-sm text-primary outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15"
            @change="applyTime"
          />
        </div>

        <!-- Footer -->
        <div class="mt-3 flex items-center justify-between border-t border-border-default pt-2.5">
          <button type="button" class="text-xs font-medium text-primary-600 hover:underline dark:text-primary-400" @click="selectToday">
            {{ timeEnabled ? 'Now' : 'Today' }}
          </button>
          <div class="flex items-center gap-2">
            <button v-if="modelValue" type="button" class="text-xs text-secondary hover:text-primary" @click="clearDate">
              Clear
            </button>
            <button
              type="button"
              class="rounded-md bg-primary-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-primary-700 dark:bg-primary-500"
              @click="isOpen = false"
            >
              Done
            </button>
          </div>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>

<script setup>
import { ref, computed, watch, inject, useAttrs } from 'vue'
import { PopoverRoot, PopoverTrigger, PopoverPortal, PopoverContent } from 'reka-ui'
import {
  Calendar as CalendarIcon, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, X, Clock,
} from 'lucide-vue-next'
import { format, isValid, startOfMonth, addMonths, isSameDay, isSameMonth } from 'date-fns'
import { cn } from '../../utils/cn'
import { formatDate, formatDateTime } from '../../utils/format'
import {
  controlBase, controlSizes, controlIdle, controlOpen, controlInvalid, controlDisabled, floatingPanel,
} from './controlStyles'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: { type: [String, null], default: '' },
  withTime: { type: Boolean, default: false },
  // Alias used by the form adapter; previously ignored, so datetime fields lost their time.
  includeTime: { type: Boolean, default: false },
  placeholder: { type: String, default: '' },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg'].includes(v),
  },
  min: { type: String, default: '' },
  max: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  invalid: { type: Boolean, default: false },
  error: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
  id: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'change', 'clear', 'blur'])

const attrs = useAttrs()
const restAttrs = computed(() => {
  const { class: _c, ...rest } = attrs
  return rest
})

const fieldCtx = inject('formField', null)
const triggerId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)
const isInvalid = computed(() => props.invalid || props.error || !!fieldCtx?.invalid?.value)
const timeEnabled = computed(() => props.withTime || props.includeTime)

const isOpen = ref(false)
const viewDate = ref(startOfMonth(new Date()))
const timeValue = ref('09:00')

const parsedDate = computed(() => {
  if (!props.modelValue) return null
  // Plain YYYY-MM-DD strings are parsed as local dates (not UTC midnight).
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(props.modelValue)
  const d = m ? new Date(+m[1], +m[2] - 1, +m[3]) : new Date(props.modelValue)
  return isValid(d) ? d : null
})

const minDate = computed(() => (props.min ? new Date(props.min) : null))
const maxDate = computed(() => (props.max ? new Date(props.max) : null))

const displayValue = computed(() => {
  if (!parsedDate.value) return ''
  return timeEnabled.value ? formatDateTime(props.modelValue) : formatDate(props.modelValue)
})

const currentMonthLabel = computed(() => format(viewDate.value, 'MMMM yyyy'))

const calendarDays = computed(() => {
  const monthStart = startOfMonth(viewDate.value)
  const offset = (monthStart.getDay() + 6) % 7
  const start = new Date(monthStart)
  start.setDate(start.getDate() - offset)
  const today = new Date()
  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const dayOnly = new Date(d.getFullYear(), d.getMonth(), d.getDate())
    return {
      key: d.toDateString(),
      date: d,
      label: format(d, 'EEEE, d MMMM yyyy'),
      isCurrentMonth: isSameMonth(d, viewDate.value),
      isToday: isSameDay(d, today),
      isSelected: parsedDate.value ? isSameDay(d, parsedDate.value) : false,
      disabled: (minDate.value && dayOnly < new Date(minDate.value.toDateString())) ||
        (maxDate.value && dayOnly > new Date(maxDate.value.toDateString())),
    }
  })
})

watch(isOpen, (open) => {
  if (!open) return
  const base = parsedDate.value || new Date()
  viewDate.value = startOfMonth(base)
  if (parsedDate.value) {
    timeValue.value = `${String(base.getHours()).padStart(2, '0')}:${String(base.getMinutes()).padStart(2, '0')}`
  }
})

function shiftMonth(n) {
  viewDate.value = addMonths(viewDate.value, n)
}

function emitDate(d) {
  let out
  if (timeEnabled.value) {
    const [h, m] = (timeValue.value || '00:00').split(':').map(Number)
    d.setHours(h || 0, m || 0, 0, 0)
    out = d.toISOString()
  } else {
    out = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }
  emit('update:modelValue', out)
  emit('change', out)
}

function selectDay(date) {
  emitDate(new Date(date))
  if (!timeEnabled.value) isOpen.value = false
}

function applyTime() {
  if (parsedDate.value) emitDate(new Date(parsedDate.value))
}

function selectToday() {
  const now = new Date()
  if (timeEnabled.value) {
    timeValue.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  }
  viewDate.value = startOfMonth(now)
  selectDay(now)
}

function clearDate() {
  emit('update:modelValue', null)
  emit('change', null)
  emit('clear')
}
</script>

<style scoped>
.nav-btn {
  @apply inline-flex h-7 w-7 items-center justify-center rounded-md text-secondary transition hover:bg-subtle hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/40;
}
</style>
