<template>
  <Card class="p-5 select-none overflow-hidden">
    <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-4">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Milestone Tracker
      </h3>
      <span v-if="isDelayed" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300">
        <AlertTriangle class="w-3 h-3" />
        Delayed ({{ delayMinutes }}m)
      </span>
      <span v-else class="text-xs text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        On Track
      </span>
    </div>

    <!-- Stepper Progress Bar -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative">
      <!-- Background Connecting Line on Desktop -->
      <div class="hidden sm:block absolute left-8 right-8 top-4 -translate-y-1/2 h-0.5 bg-slate-200 dark:bg-slate-800 -z-0">
        <div
          class="h-full bg-brand-500 transition-all duration-500"
          :style="{ width: `${progressPct}%` }"
        />
      </div>

      <!-- Step Nodes -->
      <div
        v-for="(step, idx) in steps"
        :key="step.key"
        :class="[
          'flex sm:flex-col items-center gap-3 sm:gap-2 relative z-10 w-full sm:w-auto',
          idx === activeStepIndex && 'font-bold'
        ]"
      >
        <!-- Node Circle Indicator -->
        <div
          :class="[
            'h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold transition-all shadow-xs shrink-0',
            idx < activeStepIndex
              ? 'bg-emerald-500 text-white shadow-emerald-500/20'
              : idx === activeStepIndex
                ? isDelayed
                  ? 'bg-amber-500 text-white ring-4 ring-amber-100 dark:ring-amber-950/50'
                  : 'bg-brand-600 text-white ring-4 ring-brand-100 dark:ring-brand-950/50'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-400 border border-slate-200 dark:border-slate-700'
          ]"
        >
          <Check v-if="idx < activeStepIndex" class="w-4 h-4 stroke-[3]" />
          <span v-else>{{ idx + 1 }}</span>
        </div>

        <!-- Node Labels & Timestamp -->
        <div class="flex-1 sm:text-center min-w-0">
          <p
            :class="[
              'text-xs truncate',
              idx === activeStepIndex
                ? 'text-slate-900 dark:text-slate-100 font-bold'
                : idx < activeStepIndex
                  ? 'text-slate-700 dark:text-slate-300 font-medium'
                  : 'text-slate-400 dark:text-slate-500'
            ]"
          >
            {{ step.label }}
          </p>
          <span v-if="step.timestamp" class="text-[10px] text-slate-400 font-mono block">
            {{ formatDateTime(step.timestamp) }}
          </span>
          <span v-else-if="idx === activeStepIndex" class="text-[10px] text-brand-600 dark:text-brand-400 font-semibold block">
            Current Stage
          </span>
        </div>
      </div>
    </div>
  </Card>
</template>

<script setup>
import { computed } from 'vue'
import { Check, AlertTriangle } from 'lucide-vue-next'
import Card from '../ui/Card.vue'
import { formatDateTime } from '../../utils/format'

const props = defineProps({
  currentStatus: {
    type: String,
    required: true,
  },
  delayMinutes: {
    type: Number,
    default: 0,
  },
  timestamps: {
    type: Object,
    default: () => ({}),
  },
})

const defaultFlow = [
  { key: 'pending', label: 'Pending' },
  { key: 'confirmed', label: 'Confirmed' },
  { key: 'active', label: 'In Transit' },
  { key: 'completed', label: 'Delivered' },
  { key: 'ready_for_invoice', label: 'Ready to Bill' },
  { key: 'invoiced', label: 'Invoiced' },
]

const steps = computed(() => {
  return defaultFlow.map((s) => ({
    ...s,
    timestamp: props.timestamps[s.key] || null,
  }))
})

const activeStepIndex = computed(() => {
  const idx = defaultFlow.findIndex((s) => s.key === props.currentStatus)
  return idx === -1 ? 0 : idx
})

const progressPct = computed(() => {
  if (defaultFlow.length <= 1) return 0
  return (activeStepIndex.value / (defaultFlow.length - 1)) * 100
})

const isDelayed = computed(() => props.delayMinutes > 0)
</script>
