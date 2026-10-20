<template>
  <div class="mx-auto w-full max-w-7xl space-y-6">
    <!-- Top Header & Live Auto-Refresh Bar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
      <div>
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">📡</span>
          <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Control Tower
          </h1>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Live Stream
          </span>
        </div>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Real-time fleet monitoring, exception handling, and predictive delay intervention.
        </p>
      </div>

      <!-- Auto-Refresh Controls -->
      <div class="flex flex-wrap items-center gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-1.5 shadow-xs text-xs">
        <!-- Live status & last updated -->
        <div class="flex items-center gap-1.5 px-2 text-slate-600 dark:text-slate-400">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              isPaused || !isTabVisible ? 'bg-slate-400' : 'bg-emerald-500 animate-pulse'
            ]"
          />
          <span class="font-mono tabular-nums">
            {{ isPaused ? 'Paused' : !isTabVisible ? 'Suspended (hidden)' : `Updated ${secondsAgo}s ago` }}
          </span>
        </div>

        <div class="h-4 w-[1px] bg-slate-200 dark:bg-slate-800" />

        <!-- Interval Selector -->
        <select
          v-model="pollInterval"
          class="h-7 rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-2 text-xs text-slate-700 dark:text-slate-300 cursor-pointer focus:ring-1 focus:ring-brand-500"
          :disabled="isPaused"
        >
          <option :value="15000">15s</option>
          <option :value="30000">30s</option>
          <option :value="60000">60s</option>
        </select>

        <!-- Pause / Resume Button -->
        <button
          type="button"
          class="h-7 px-2.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium flex items-center gap-1 transition-colors cursor-pointer"
          @click="togglePause"
        >
          <component :is="isPaused ? Play : Pause" class="w-3.5 h-3.5" />
          <span>{{ isPaused ? 'Resume' : 'Pause' }}</span>
        </button>

        <!-- Manual Refresh Button -->
        <button
          type="button"
          class="h-7 w-7 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center transition-colors cursor-pointer"
          title="Refresh now"
          :disabled="loading"
          @click="fetchData"
        >
          <RefreshCw :class="['w-3.5 h-3.5', loading && 'animate-spin text-brand-600']" />
        </button>
      </div>
    </div>

    <!-- Live Status Tiles (Clickable Filters) -->
    <div v-if="data?.tiles" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
      <!-- On the Road -->
      <div
        :class="[
          'p-4 rounded-xl border bg-white dark:bg-slate-900 shadow-xs cursor-pointer transition-all select-none',
          selectedTile === 'on_road'
            ? 'border-brand-500 ring-2 ring-brand-500/20'
            : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
        ]"
        @click="selectTile('on_road')"
      >
        <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">On the Road</span>
        <div class="mt-1 text-2xl sm:text-3xl font-bold font-mono text-slate-900 dark:text-slate-100">
          {{ data.tiles.on_road }}
        </div>
        <p class="text-[11px] text-slate-500 mt-1">Trips in transit now</p>
      </div>

      <!-- At Risk (Delayed or Missing ETA) -->
      <div
        :class="[
          'p-4 rounded-xl border bg-white dark:bg-slate-900 shadow-xs cursor-pointer transition-all select-none',
          selectedTile === 'at_risk'
            ? 'border-rose-500 ring-2 ring-rose-500/20'
            : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
        ]"
        @click="selectTile('at_risk')"
      >
        <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">At Risk</span>
        <div :class="['mt-1 text-2xl sm:text-3xl font-bold font-mono', data.tiles.at_risk > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-slate-100']">
          {{ data.tiles.at_risk }}
        </div>
        <p class="text-[11px] text-slate-500 mt-1">Late or ETA past plan</p>
      </div>

      <!-- Need a Truck (<24h) -->
      <div
        :class="[
          'p-4 rounded-xl border bg-white dark:bg-slate-900 shadow-xs cursor-pointer transition-all select-none',
          selectedTile === 'need_truck'
            ? 'border-amber-500 ring-2 ring-amber-500/20'
            : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
        ]"
        @click="selectTile('need_truck')"
      >
        <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Need a Truck</span>
        <div :class="['mt-1 text-2xl sm:text-3xl font-bold font-mono', data.tiles.need_truck > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-900 dark:text-slate-100']">
          {{ data.tiles.need_truck }}
        </div>
        <p class="text-[11px] text-slate-500 mt-1">Departing in &lt;24 hours</p>
      </div>

      <!-- GPS Silent (>30m) -->
      <div
        :class="[
          'p-4 rounded-xl border bg-white dark:bg-slate-900 shadow-xs cursor-pointer transition-all select-none',
          selectedTile === 'gps_silent'
            ? 'border-rose-500 ring-2 ring-rose-500/20'
            : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
        ]"
        @click="selectTile('gps_silent')"
      >
        <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">GPS Silent</span>
        <div :class="['mt-1 text-2xl sm:text-3xl font-bold font-mono', data.tiles.gps_silent > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-slate-100']">
          {{ data.tiles.gps_silent }}
        </div>
        <p class="text-[11px] text-slate-500 mt-1">No telematics &gt;30 min</p>
      </div>

      <!-- Idle Trucks -->
      <div
        :class="[
          'p-4 rounded-xl border bg-white dark:bg-slate-900 shadow-xs cursor-pointer transition-all select-none',
          selectedTile === 'idle'
            ? 'border-brand-500 ring-2 ring-brand-500/20'
            : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
        ]"
        @click="selectTile('idle')"
      >
        <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Idle Own Trucks</span>
        <div class="mt-1 text-2xl sm:text-3xl font-bold font-mono text-slate-900 dark:text-slate-100">
          {{ data.tiles.idle }}
        </div>
        <p class="text-[11px] text-slate-500 mt-1">Active & ready for dispatch</p>
      </div>
    </div>

    <!-- Toolbar: Search, Branch, Delayed Only, Density, View Switcher -->
    <div class="p-3 sm:p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
      <!-- Search & Branch Filter -->
      <div class="flex flex-wrap items-center gap-2.5 flex-1 min-w-[280px]">
        <div class="relative w-full sm:w-64">
          <Search class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search trips, trucks, drivers…"
            class="w-full pl-8 pr-3 py-1.5 text-xs rounded-md border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>

        <Combobox
          v-model="branch"
          :options="branchOptions"
          placeholder="All branches"
          class="!w-44"
        />

        <!-- Delayed Only Toggle -->
        <label class="inline-flex items-center gap-2 cursor-pointer select-none text-slate-700 dark:text-slate-300 font-medium">
          <input
            type="checkbox"
            v-model="delayedOnly"
            class="rounded border-slate-300 text-brand-600 focus:ring-brand-500 h-4 w-4"
          />
          <span>Delayed only</span>
        </label>
      </div>

      <!-- Right Controls: Density and View Toggle -->
      <div class="flex items-center gap-2">
        <!-- Density -->
        <div class="inline-flex rounded-lg border border-slate-200 dark:border-slate-800 p-0.5 text-xs">
          <button
            type="button"
            :class="[
              'px-2.5 py-1 rounded-md transition-colors',
              density === 'compact' ? 'bg-brand-600 text-white font-medium' : 'text-slate-500 hover:text-slate-900'
            ]"
            @click="density = 'compact'"
          >
            Compact
          </button>
          <button
            type="button"
            :class="[
              'px-2.5 py-1 rounded-md transition-colors',
              density === 'normal' ? 'bg-brand-600 text-white font-medium' : 'text-slate-500 hover:text-slate-900'
            ]"
            @click="density = 'normal'"
          >
            Normal
          </button>
        </div>

        <!-- Board vs List View Toggle -->
        <div class="inline-flex rounded-lg border border-slate-200 dark:border-slate-800 p-0.5 text-xs">
          <button
            type="button"
            :class="[
              'px-2.5 py-1 rounded-md flex items-center gap-1.5 transition-colors',
              viewMode === 'board' ? 'bg-brand-600 text-white font-medium' : 'text-slate-500 hover:text-slate-900'
            ]"
            @click="viewMode = 'board'"
          >
            <Columns3 class="w-3.5 h-3.5" />
            <span>Board</span>
          </button>
          <button
            type="button"
            :class="[
              'px-2.5 py-1 rounded-md flex items-center gap-1.5 transition-colors',
              viewMode === 'list' ? 'bg-brand-600 text-white font-medium' : 'text-slate-500 hover:text-slate-900'
            ]"
            @click="viewMode = 'list'"
          >
            <List class="w-3.5 h-3.5" />
            <span>List</span>
          </button>
        </div>
      </div>
    </div>

    <!-- MAIN VIEW 1: LIVE KANBAN BOARD -->
    <div
      v-if="viewMode === 'board'"
      class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 overflow-x-auto pb-4"
    >
      <!-- Column 1: Unassigned / Needs Truck -->
      <div class="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/40 p-3 space-y-3 flex flex-col min-h-[500px]">
        <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-amber-500" />
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
              Needs Truck
            </h3>
          </div>
          <span class="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300">
            {{ unassignedTrips.length }}
          </span>
        </div>

        <div class="space-y-3 flex-1 overflow-y-auto max-h-[700px] pr-1">
          <TripCard
            v-for="trip in unassignedTrips"
            :key="trip.id"
            :trip="trip"
            :density="density"
            @click="openQuickView(trip)"
          />
          <div v-if="!unassignedTrips.length" class="py-12 text-center text-xs text-slate-400">
            All departures have assigned trucks ✓
          </div>
        </div>
      </div>

      <!-- Column 2: Scheduled (<24h Departures) -->
      <div class="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/40 p-3 space-y-3 flex flex-col min-h-[500px]">
        <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-sky-500" />
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
              Scheduled
            </h3>
          </div>
          <span class="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-sky-100 text-sky-800 dark:bg-sky-950/60 dark:text-sky-300">
            {{ scheduledTrips.length }}
          </span>
        </div>

        <div class="space-y-3 flex-1 overflow-y-auto max-h-[700px] pr-1">
          <TripCard
            v-for="trip in scheduledTrips"
            :key="trip.id"
            :trip="trip"
            :density="density"
            @click="openQuickView(trip)"
          />
          <div v-if="!scheduledTrips.length" class="py-12 text-center text-xs text-slate-400">
            No scheduled departures in next 24h.
          </div>
        </div>
      </div>

      <!-- Column 3: On The Road (In Transit) -->
      <div class="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/40 p-3 space-y-3 flex flex-col min-h-[500px]">
        <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
              On Road (Normal)
            </h3>
          </div>
          <span class="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
            {{ onRoadNormalTrips.length }}
          </span>
        </div>

        <div class="space-y-3 flex-1 overflow-y-auto max-h-[700px] pr-1">
          <TripCard
            v-for="trip in onRoadNormalTrips"
            :key="trip.id"
            :trip="trip"
            :density="density"
            @click="openQuickView(trip)"
          />
          <div v-if="!onRoadNormalTrips.length" class="py-12 text-center text-xs text-slate-400">
            No trips currently on road.
          </div>
        </div>
      </div>

      <!-- Column 4: At Risk / Critical Exceptions -->
      <div class="rounded-xl border border-rose-200 dark:border-rose-900/60 bg-rose-50/30 dark:bg-rose-950/20 p-3 space-y-3 flex flex-col min-h-[500px]">
        <div class="flex items-center justify-between pb-2 border-b border-rose-200 dark:border-rose-900/60">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
            <h3 class="text-xs font-bold uppercase tracking-wider text-rose-900 dark:text-rose-200">
              At Risk / Delayed
            </h3>
          </div>
          <span class="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-200">
            {{ atRiskTrips.length }}
          </span>
        </div>

        <div class="space-y-3 flex-1 overflow-y-auto max-h-[700px] pr-1">
          <TripCard
            v-for="trip in atRiskTrips"
            :key="trip.id"
            :trip="trip"
            :density="density"
            @click="openQuickView(trip)"
          />
          <div v-if="!atRiskTrips.length" class="py-12 text-center text-xs text-emerald-600 font-semibold">
            Zero transit exceptions right now ✓
          </div>
        </div>
      </div>
    </div>

    <!-- MAIN VIEW 2: TABULAR LIST -->
    <Card v-else class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead class="bg-slate-50 dark:bg-slate-800/60 text-[11px] font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200 dark:border-slate-800">
            <tr>
              <th class="px-4 py-3">Trip #</th>
              <th class="px-4 py-3">Order</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3">Risk</th>
              <th class="px-4 py-3">Lane & Customer</th>
              <th class="px-4 py-3">Truck & Driver</th>
              <th class="px-4 py-3">ETA</th>
              <th class="px-4 py-3">Delay</th>
              <th class="px-4 py-3 text-right">GPS</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800/60">
            <tr
              v-for="c in filteredListTrips"
              :key="c.id"
              class="hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors"
              @click="openQuickView(c)"
            >
              <td class="px-4 py-3 font-mono font-bold text-slate-900 dark:text-slate-100">{{ c.number }}</td>
              <td class="px-4 py-3 font-mono text-brand-600 dark:text-brand-400">#{{ c.order }}</td>
              <td class="px-4 py-3">
                <StatusPill :status="c.status" size="sm" />
              </td>
              <td class="px-4 py-3">
                <span
                  :class="[
                    'px-2 py-0.5 rounded-full text-[10px] font-bold capitalize',
                    c.risk === 'late'
                      ? 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300'
                      : c.risk === 'on_track'
                        ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                        : 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
                  ]"
                >
                  {{ c.risk.replace('_', ' ') }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span class="font-semibold block text-slate-900 dark:text-slate-100">{{ c.lane }}</span>
                <span class="text-slate-400 text-[11px]">{{ c.customer }}</span>
              </td>
              <td class="px-4 py-3 font-mono">
                <span class="block text-slate-900 dark:text-slate-100">{{ c.truck || 'Needs truck' }}</span>
                <span class="text-slate-400 text-[11px] font-sans">{{ c.driver || 'No driver' }}</span>
              </td>
              <td class="px-4 py-3 font-mono text-slate-600 dark:text-slate-400">
                {{ c.eta ? formatDateTime(c.eta) : '—' }}
              </td>
              <td class="px-4 py-3">
                <span v-if="c.delay_minutes" class="text-rose-600 font-bold">+{{ c.delay_minutes }}m</span>
                <span v-else class="text-emerald-600">On time</span>
              </td>
              <td class="px-4 py-3 text-right">
                <span :class="['font-bold text-[11px]', c.gps === 'ok' ? 'text-emerald-600' : 'text-rose-600']">
                  {{ c.gps }}
                </span>
              </td>
            </tr>
            <tr v-if="!filteredListTrips.length">
              <td colspan="9" class="p-8 text-center text-slate-400">
                No trips matching current filters.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Slide-over Quick View Drawer for Selected Trip -->
    <ResourceQuickView
      :open="isDrawerOpen"
      :record="selectedTripRecord"
      resource-key="trips"
      :meta="tripMeta"
      @update:open="isDrawerOpen = $event"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useDocumentVisibility } from '@vueuse/core'
import {
  Play,
  Pause,
  RefreshCw,
  Search,
  Columns3,
  List,
} from 'lucide-vue-next'
import api, { errText } from '../api'
import { formatDateTime } from '../utils/format'

import Card from '../components/ui/Card.vue'
import Combobox from '../components/ui/Combobox.vue'
import StatusPill from '../components/ui/StatusPill.vue'
import TripCard from '../components/control-tower/TripCard.vue'
import ResourceQuickView from '../components/resource/ResourceQuickView.vue'

// State
const data = ref(null)
const loading = ref(false)
const branch = ref(null)
const branchOptions = ref([])
const selectedTile = ref('on_road')
const viewMode = ref('board') // 'board' | 'list'
const density = ref('normal') // 'compact' | 'normal'
const searchQuery = ref('')
const delayedOnly = ref(false)

// Polling & Visibility
const pollInterval = ref(30000)
const isPaused = ref(false)
const now = ref(Date.now())
const visibility = useDocumentVisibility()
const isTabVisible = computed(() => visibility.value === 'visible')

let pollTimer = null
let secondTicker = null

const secondsAgo = computed(() => {
  if (!data.value?.updated_at) return 0
  return Math.max(0, Math.round((now.value - new Date(data.value.updated_at).getTime()) / 1000))
})

// Drawer State
const isDrawerOpen = ref(false)
const selectedTripRecord = ref(null)
const tripMeta = ref({
  key: 'trips',
  title: 'Trips',
  icon: '🚚',
  columns: ['number', 'order', 'status', 'lane', 'vehicle', 'driver', 'planned_start', 'eta', 'delay_minutes'],
  fields: {
    number: { label: 'Trip #' },
    order: { label: 'Order #' },
    status: { label: 'Status' },
    lane: { label: 'Lane' },
    vehicle: { label: 'Vehicle' },
    driver: { label: 'Driver' },
    planned_start: { label: 'Planned Start', type: 'datetime' },
    eta: { label: 'ETA', type: 'datetime' },
    delay_minutes: { label: 'Delay (min)' },
  },
})

function openQuickView(trip) {
  selectedTripRecord.value = {
    ...trip,
    status_label: trip.status?.replace('_', ' ').toUpperCase(),
  }
  isDrawerOpen.value = true
}

// Filtered Lists for Kanban Columns
const allTrips = computed(() => {
  if (!data.value) return []
  const onRoad = data.value.on_road || []
  const departures = data.value.departures || []
  const map = new Map()
  for (const t of [...onRoad, ...departures]) {
    map.set(t.id, t)
  }
  return Array.from(map.values())
})

const matchesSearchAndFilter = (t) => {
  if (delayedOnly.value && (t.delay_minutes || 0) < 15 && t.risk !== 'late') {
    return false
  }
  if (!searchQuery.value) return true
  const q = searchQuery.value.toLowerCase()
  return (
    t.number?.toLowerCase().includes(q) ||
    t.order?.toLowerCase().includes(q) ||
    t.customer?.toLowerCase().includes(q) ||
    t.lane?.toLowerCase().includes(q) ||
    t.truck?.toLowerCase().includes(q) ||
    t.driver?.toLowerCase().includes(q)
  )
}

const unassignedTrips = computed(() => {
  return (data.value?.departures || [])
    .filter((t) => t.status === 'unassigned')
    .filter(matchesSearchAndFilter)
})

const scheduledTrips = computed(() => {
  return (data.value?.departures || [])
    .filter((t) => t.status !== 'unassigned')
    .filter(matchesSearchAndFilter)
})

const onRoadNormalTrips = computed(() => {
  return (data.value?.on_road || [])
    .filter((t) => t.risk === 'on_track')
    .filter(matchesSearchAndFilter)
})

const atRiskTrips = computed(() => {
  return (data.value?.on_road || [])
    .filter((t) => ['late', 'at_risk', 'no_eta'].includes(t.risk))
    .filter(matchesSearchAndFilter)
})

const filteredListTrips = computed(() => {
  if (!data.value) return []
  let list = allTrips.value
  if (selectedTile.value === 'at_risk') {
    list = list.filter((t) => t.risk !== 'on_track')
  } else if (selectedTile.value === 'gps_silent') {
    list = list.filter((t) => t.gps === 'silent')
  } else if (selectedTile.value === 'need_truck') {
    list = list.filter((t) => t.status === 'unassigned')
  }
  return list.filter(matchesSearchAndFilter)
})

function selectTile(tileKey) {
  selectedTile.value = tileKey
}

function togglePause() {
  isPaused.value = !isPaused.value
  if (!isPaused.value) {
    fetchData()
    resetTimer()
  } else {
    clearInterval(pollTimer)
  }
}

function resetTimer() {
  clearInterval(pollTimer)
  if (!isPaused.value && isTabVisible.value) {
    pollTimer = setInterval(fetchData, pollInterval.value)
  }
}

watch([pollInterval, isTabVisible], () => {
  resetTimer()
})

async function fetchData() {
  loading.value = true
  try {
    const params = {}
    if (branch.value) params.branch = branch.value
    const res = await api.get('control-tower/', { params })
    data.value = res.data
  } catch (e) {
    console.warn('Control tower poll failed:', errText(e))
  } finally {
    loading.value = false
  }
}

async function loadBranches() {
  try {
    const res = await api.get('branches/', { params: { page_size: 200 } })
    branchOptions.value = [
      { value: null, label: 'All branches' },
      ...(res.data.results || []).map((b) => ({ value: b.id, label: b.name })),
    ]
  } catch {}
}

watch(branch, () => {
  fetchData()
})

onMounted(() => {
  loadBranches()
  fetchData()
  resetTimer()
  secondTicker = setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  clearInterval(pollTimer)
  clearInterval(secondTicker)
})
</script>
