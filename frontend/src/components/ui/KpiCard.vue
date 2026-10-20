<template>
  <div
    :class="cn(
      'rounded-lg border border-border-default bg-surface p-4 shadow-xs transition-all flex flex-col justify-between',
      clickable && 'cursor-pointer hover:border-primary-400 hover:shadow-sm active:scale-[0.99]',
      $attrs.class
    )"
  >
    <!-- Top Row: Label and info/sparkline -->
    <div class="flex items-center justify-between gap-2">
      <span class="text-xs font-semibold uppercase tracking-wider text-secondary truncate">
        {{ label || title }}
      </span>

      <!-- Mini inline sparkline SVG if provided -->
      <svg
        v-if="sparkline && sparkline.length >= 2 && !loading"
        class="w-16 h-6 stroke-primary-600 dark:stroke-primary-400 overflow-visible shrink-0"
        fill="none"
        viewBox="0 0 60 20"
      >
        <path
          :d="sparklinePath"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </div>

    <!-- Middle Row: Main Metric Value -->
    <div class="mt-2">
      <Skeleton v-if="loading" size="lg" width="w-28" />
      <div v-else class="flex flex-wrap items-baseline gap-1 text-2xl font-bold tracking-tight text-primary tabular-nums xl:text-[28px]">
        <span>{{ formattedValue }}</span>
        <span v-if="unit" class="text-xs font-medium text-secondary">{{ unit }}</span>
      </div>
    </div>

    <!-- Bottom: delta on one line, context on the next (never truncated mid-word) -->
    <div class="mt-3 flex flex-col gap-1 text-xs">
      <Skeleton v-if="loading" size="sm" width="w-36" />
      <template v-else>
        <!-- Delta Badge -->
        <div
          v-if="delta !== null && delta !== undefined"
          :class="cn('flex items-center gap-1 font-semibold tabular-nums', deltaColorClass)"
        >
          <TrendingUp v-if="delta > 0" class="w-3.5 h-3.5 shrink-0" />
          <TrendingDown v-else-if="delta < 0" class="w-3.5 h-3.5 shrink-0" />
          <Minus v-else class="w-3.5 h-3.5 shrink-0" />

          <span class="whitespace-nowrap">{{ delta > 0 ? '+' : '' }}{{ delta }}{{ isPts ? ' pts' : '%' }}</span>
          <span class="ml-0.5 whitespace-nowrap text-[11px] font-normal text-muted">{{ deltaPeriod }}</span>
        </div>
        <span v-else class="text-muted text-[11px]">No prior data</span>

        <!-- Optional Subtitle/Context -->
        <span v-if="subtitle" class="line-clamp-2 text-[11px] leading-snug text-muted" :title="subtitle">
          {{ subtitle }}
        </span>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TrendingUp, TrendingDown, Minus } from 'lucide-vue-next'
import { cn } from '../../utils/cn'
import Skeleton from '../feedback/Skeleton.vue'

const props = defineProps({
  title: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  value: {
    type: [Number, String, null],
    default: null,
  },
  unit: {
    type: String,
    default: '',
  },
  delta: {
    type: [Number, null],
    default: null,
  },
  deltaPeriod: {
    type: String,
    default: 'vs prev',
  },
  isPts: {
    type: Boolean,
    default: false,
  },
  goodDirection: {
    type: String,
    default: 'up',
    validator: v => ['up', 'down'].includes(v),
  },
  subtitle: {
    type: String,
    default: '',
  },
  sparkline: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  clickable: {
    type: Boolean,
    default: false,
  },
})

const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined || props.value === '') return '—'
  return props.value
})

const deltaColorClass = computed(() => {
  if (props.delta === null || props.delta === undefined || props.delta === 0) {
    return 'text-secondary'
  }
  const isPositive = props.delta > 0
  const isGood = props.goodDirection === 'up' ? isPositive : !isPositive
  return isGood
    ? 'text-success-600 dark:text-success-500'
    : 'text-danger-600 dark:text-danger-500'
})

const sparklinePath = computed(() => {
  const data = props.sparkline
  if (!data || data.length < 2) return ''
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const width = 60
  const height = 20

  const points = data.map((val, idx) => {
    const x = (idx / (data.length - 1)) * width
    const y = height - ((val - min) / range) * (height - 4) - 2
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })

  return `M ${points.join(' L ')}`
})
</script>
