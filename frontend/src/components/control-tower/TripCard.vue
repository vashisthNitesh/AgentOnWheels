<template>
  <div
    :class="[
      'rounded-xl border bg-white dark:bg-slate-900 shadow-xs hover:shadow-md transition-all cursor-pointer group select-none',
      density === 'compact' ? 'p-3 space-y-2' : 'p-4 space-y-3',
      trip.risk === 'late'
        ? 'border-rose-300 dark:border-rose-900/60 hover:border-rose-500'
        : trip.risk === 'at_risk' || trip.risk === 'no_eta'
          ? 'border-amber-300 dark:border-amber-900/60 hover:border-amber-500'
          : 'border-slate-200 dark:border-slate-800 hover:border-brand-500/60'
    ]"
    @click="$emit('click', trip)"
  >
    <!-- Top Row: Trip Number & Status / Risk Badge -->
    <div class="flex items-center justify-between gap-2">
      <div class="flex items-center gap-1.5 min-w-0">
        <span class="font-mono text-xs font-bold text-slate-900 dark:text-slate-100 truncate">
          {{ trip.number }}
        </span>
        <router-link
          v-if="trip.order_id"
          :to="`/orders/${trip.order_id}`"
          class="font-mono text-[10px] text-brand-600 dark:text-brand-400 hover:underline"
          @click.stop
        >
          ({{ trip.order }})
        </router-link>
      </div>

      <!-- Risk / Delay Badge -->
      <div class="flex items-center gap-1 shrink-0">
        <!-- Delay Badge -->
        <span
          v-if="trip.delay_minutes >= DELAY_DANGER_MIN"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300"
          title="Critical delay ≥ 60m"
        >
          <AlertOctagon class="w-3 h-3" />
          +{{ trip.delay_minutes }}m
        </span>
        <span
          v-else-if="trip.delay_minutes >= DELAY_WARN_MIN"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300"
          title="Warning delay ≥ 15m"
        >
          <AlertTriangle class="w-3 h-3" />
          +{{ trip.delay_minutes }}m
        </span>
        <span
          v-else-if="trip.risk === 'on_track'"
          class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          On track
        </span>
        <span
          v-else-if="trip.risk === 'no_eta'"
          class="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
        >
          No ETA
        </span>
      </div>
    </div>

    <!-- Route Lane & Customer -->
    <div class="space-y-0.5 text-xs">
      <div class="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1 truncate">
        <MapPin class="w-3 h-3 text-brand-600 dark:text-brand-400 shrink-0" />
        <span class="truncate">{{ trip.lane }}</span>
      </div>
      <p class="text-[11px] text-slate-500 dark:text-slate-400 truncate pl-4">
        {{ trip.customer }} · {{ trip.job_type }}
      </p>
    </div>

    <!-- Driver & Vehicle Row -->
    <div class="pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs">
      <!-- Driver with Avatar -->
      <div class="flex items-center gap-1.5 min-w-0">
        <Avatar :name="trip.driver || 'Driver'" size="xs" />
        <span class="truncate font-medium text-slate-700 dark:text-slate-300 max-w-[90px]">
          {{ trip.driver || 'No driver' }}
        </span>
      </div>

      <!-- Vehicle Plate or Market Truck -->
      <div class="flex items-center gap-1 text-[11px] font-mono font-medium text-slate-600 dark:text-slate-400 shrink-0">
        <Truck class="w-3 h-3 text-slate-400" />
        <span>{{ trip.truck || 'Needs truck' }}</span>
      </div>
    </div>

    <!-- Bottom ETA & GPS Footer -->
    <div class="flex items-center justify-between text-[10px] text-slate-400 font-medium pt-1">
      <!-- ETA -->
      <Tooltip :content="trip.eta ? formatDateTime(trip.eta) : 'ETA not reported by driver or telematics'">
        <span class="inline-flex items-center gap-1 cursor-default">
          <Clock class="w-3 h-3" />
          <span>ETA: {{ trip.eta ? formatRelative(trip.eta) : '—' }}</span>
        </span>
      </Tooltip>

      <!-- GPS Health -->
      <span
        :class="[
          'inline-flex items-center gap-1 font-semibold',
          trip.gps === 'ok' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'
        ]"
      >
        <Radio :class="['w-3 h-3', trip.gps === 'ok' && 'animate-pulse']" />
        <span>GPS {{ trip.gps }}</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import {
  MapPin,
  Truck,
  Clock,
  Radio,
  AlertTriangle,
  AlertOctagon,
} from 'lucide-vue-next'
import Avatar from '../ui/Avatar.vue'
import Tooltip from '../ui/Tooltip.vue'
import { formatRelative, formatDateTime } from '../../utils/format'

const DELAY_WARN_MIN = 15
const DELAY_DANGER_MIN = 60

defineProps({
  trip: {
    type: Object,
    required: true,
  },
  density: {
    type: String,
    default: 'normal',
  },
})

defineEmits(['click'])
</script>
