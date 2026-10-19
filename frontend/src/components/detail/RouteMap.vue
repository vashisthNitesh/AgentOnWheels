<template>
  <Card class="p-5 space-y-4 overflow-hidden relative">
    <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
      <div class="flex items-center gap-2">
        <MapPin class="w-4 h-4 text-brand-600 dark:text-brand-400" />
        <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Route & Transit Corridor</h3>
      </div>
      <div class="flex items-center gap-2 text-xs text-slate-500 font-mono">
        <span v-if="distanceKm" class="font-semibold text-slate-800 dark:text-slate-200">{{ distanceKm }} km</span>
        <span v-if="serviceType" class="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] uppercase font-bold tracking-wider">
          {{ serviceType }}
        </span>
      </div>
    </div>

    <!-- Stylized Route Diagram -->
    <div class="relative py-4 px-2">
      <!-- Route line -->
      <div class="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
        <div class="h-full bg-brand-500 w-2/3 rounded-full" />
      </div>

      <!-- Stops -->
      <div class="relative flex items-center justify-between">
        <!-- Origin Point -->
        <div class="flex flex-col items-center gap-1.5 text-center max-w-[120px]">
          <div class="h-6 w-6 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-md ring-4 ring-emerald-100 dark:ring-emerald-950/60 z-10">
            <span class="text-[10px] font-bold">A</span>
          </div>
          <span class="text-xs font-bold text-slate-900 dark:text-slate-100 truncate w-full" :title="source">
            {{ source || 'Origin' }}
          </span>
          <span class="text-[10px] text-slate-400">Pickup</span>
        </div>

        <!-- Transit Waypoint -->
        <div v-if="via" class="flex flex-col items-center gap-1.5 text-center max-w-[100px]">
          <div class="h-4 w-4 rounded-full bg-brand-500 text-white flex items-center justify-center text-[9px] font-bold ring-2 ring-brand-100 dark:ring-brand-950/50 z-10">
            •
          </div>
          <span class="text-[11px] font-medium text-slate-600 dark:text-slate-300 truncate w-full">
            Via {{ via }}
          </span>
          <span class="text-[10px] text-slate-400">Waypoint</span>
        </div>

        <!-- Destination Point -->
        <div class="flex flex-col items-center gap-1.5 text-center max-w-[120px]">
          <div class="h-6 w-6 rounded-full bg-rose-500 text-white flex items-center justify-center shadow-md ring-4 ring-rose-100 dark:ring-rose-950/60 z-10">
            <span class="text-[10px] font-bold">B</span>
          </div>
          <span class="text-xs font-bold text-slate-900 dark:text-slate-100 truncate w-full" :title="destination">
            {{ destination || 'Destination' }}
          </span>
          <span class="text-[10px] text-slate-400">Offload</span>
        </div>
      </div>
    </div>

    <!-- Stops Details Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-1">
        <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 block">
          Pickup Address
        </span>
        <p class="font-medium text-slate-900 dark:text-slate-100">
          {{ pickupAddress || 'Standard Warehouse Terminal' }}
        </p>
        <p v-if="pickupContact" class="text-slate-500 text-[11px]">Contact: {{ pickupContact }}</p>
        <p v-if="loadCutoff" class="text-slate-400 text-[10px]">Load cut-off: {{ formatDate(loadCutoff) }}</p>
      </div>

      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-1">
        <span class="text-[10px] font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400 block">
          Delivery Address
        </span>
        <p class="font-medium text-slate-900 dark:text-slate-100">
          {{ dropAddress || 'Consignee Receiving Bay' }}
        </p>
        <p v-if="dropContact" class="text-slate-500 text-[11px]">Contact: {{ dropContact }}</p>
        <p v-if="offloadCutoff" class="text-slate-400 text-[10px]">Offload cut-off: {{ formatDate(offloadCutoff) }}</p>
      </div>
    </div>
  </Card>
</template>

<script setup>
import { MapPin } from 'lucide-vue-next'
import Card from '../ui/Card.vue'
import { formatDate } from '../../utils/format'

defineProps({
  source: String,
  destination: String,
  via: String,
  distanceKm: [Number, String],
  serviceType: String,
  pickupAddress: String,
  pickupContact: String,
  loadCutoff: String,
  dropAddress: String,
  dropContact: String,
  offloadCutoff: String,
})
</script>
