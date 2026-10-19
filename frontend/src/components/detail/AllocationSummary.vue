<template>
  <Card class="p-5 space-y-4">
    <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Asset & Driver Allocation
      </h3>
      <span
        :class="[
          'px-2 py-0.5 rounded-full text-[11px] font-semibold',
          allocationStatus === 'fully_allocated'
            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300'
            : 'bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300'
        ]"
      >
        {{ allocationStatus === 'fully_allocated' ? 'Fully Allocated' : (allocationStatus || 'Pending') }}
      </span>
    </div>

    <!-- Vehicles Commitment Gauge -->
    <div class="space-y-1.5">
      <div class="flex justify-between text-xs">
        <span class="text-slate-500 dark:text-slate-400">Vehicle Commitment</span>
        <span class="font-bold text-slate-900 dark:text-slate-100 font-mono">
          {{ vehiclesCommitted }} of {{ numVehicles }} committed
        </span>
      </div>
      <div class="h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
        <div
          class="h-full bg-brand-500 rounded-full transition-all duration-300"
          :style="{ width: `${commitmentPct}%` }"
        />
      </div>
    </div>

    <!-- Assigned Driver & Primary Truck -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
      <!-- Driver Info -->
      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 flex items-center gap-3">
        <Avatar :name="driverName || 'Driver'" size="md" />
        <div class="min-w-0">
          <span class="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">Driver</span>
          <p class="font-semibold text-slate-900 dark:text-slate-100 truncate">
            {{ driverName || 'Unassigned' }}
          </p>
          <p v-if="driverPhone" class="text-slate-500 text-[11px] font-mono">{{ driverPhone }}</p>
        </div>
      </div>

      <!-- Vehicle Info -->
      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 flex items-center gap-3">
        <div class="h-9 w-9 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300 shrink-0">
          <Truck class="w-4 h-4" />
        </div>
        <div class="min-w-0">
          <span class="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">Primary Vehicle</span>
          <p class="font-semibold text-slate-900 dark:text-slate-100 truncate font-mono">
            {{ vehiclePlate || 'Market/Pending' }}
          </p>
          <p v-if="trailerOrContainer" class="text-slate-500 text-[11px] truncate">{{ trailerOrContainer }}</p>
        </div>
      </div>
    </div>

    <!-- Cargo Weight Utilization -->
    <div v-if="weightT" class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-1.5 text-xs">
      <div class="flex justify-between">
        <span class="text-slate-500 dark:text-slate-400">Cargo Weight Capacity</span>
        <span class="font-bold text-slate-900 dark:text-slate-100 font-mono">{{ weightT }} tonnes</span>
      </div>
      <div class="h-1.5 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
        <div class="h-full bg-emerald-500 rounded-full" style="width: 78%;" />
      </div>
    </div>
  </Card>
</template>

<script setup>
import { computed } from 'vue'
import { Truck } from 'lucide-vue-next'
import Card from '../ui/Card.vue'
import Avatar from '../ui/Avatar.vue'

const props = defineProps({
  vehiclesCommitted: {
    type: Number,
    default: 0,
  },
  numVehicles: {
    type: Number,
    default: 1,
  },
  allocationStatus: String,
  driverName: String,
  driverPhone: String,
  vehiclePlate: String,
  trailerOrContainer: String,
  weightT: [Number, String],
})

const commitmentPct = computed(() => {
  if (!props.numVehicles) return 0
  return Math.min(100, Math.round((props.vehiclesCommitted / props.numVehicles) * 100))
})
</script>
