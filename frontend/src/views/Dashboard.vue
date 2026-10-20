<template>
  <div class="mx-auto w-full max-w-7xl space-y-6">
    <!-- Sticky Global Filter Bar -->
    <div class="sticky top-0 z-20 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md shadow-xs space-y-3">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <!-- Title & Period Subtitle -->
        <div>
          <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <span>Operations dashboard</span>
          </h1>
          <p v-if="dashboardData?.period" class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            {{ formatDate(dashboardData.period.start) }} – {{ formatDate(dashboardData.period.end) }}
            <span class="text-slate-400">vs</span>
            {{ formatDate(dashboardData.period.prev_start) }} – {{ formatDate(dashboardData.period.prev_end) }}
          </p>
        </div>

        <!-- Controls Row -->
        <div class="flex flex-wrap items-center gap-2">
          <!-- Preset Buttons -->
          <div class="inline-flex rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 p-0.5 text-xs font-semibold">
            <button
              v-for="r in ['7d', '30d', '90d', 'mtd']"
              :key="r"
              type="button"
              :class="[
                'px-2.5 py-1 rounded-md transition-all cursor-pointer',
                range === r && !from && !to
                  ? 'bg-primary-600 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              ]"
              @click="setPresetRange(r)"
            >
              {{ r.toUpperCase() }}
            </button>
          </div>

          <!-- Custom Date Inputs -->
          <DateRangePicker
            v-model:start-value="from"
            v-model:end-value="to"
            size="sm"
            placeholder="Custom range"
            class="w-[230px]"
          />

          <!-- Reset Filters Button -->
          <button
            v-if="hasActiveFilters"
            type="button"
            class="h-8 px-2.5 text-xs font-medium text-rose-600 dark:text-rose-400 hover:underline"
            @click="resetFilters"
          >
            Reset
          </button>
        </div>
      </div>

      <!-- Secondary Filter Row: Branch, Customer, Job Type -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 border-t border-slate-100 dark:border-slate-800/80">
        <!-- Branch Selector -->
        <Combobox
          v-model="branch"
          :options="branchOptions"
          placeholder="All branches"
        />

        <!-- Customer Selector -->
        <Combobox
          v-model="customer"
          :options="customerOptions"
          placeholder="All customers"
        />

        <!-- Job Type Selector -->
        <Select
          v-model="jobType"
          :options="[
            { value: '', label: 'All job types' },
            { value: 'FTL', label: 'FTL (Full Truckload)' },
            { value: 'LTL', label: 'LTL (Less than Truckload)' },
            { value: 'FCL', label: 'FCL (Full Container Load)' },
          ]"
          placeholder="All job types"
        />
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="p-6 rounded-xl border border-rose-200 bg-rose-50 text-rose-800 text-center space-y-3">
      <p class="text-sm font-semibold">{{ error }}</p>
      <Button variant="outline" size="sm" @click="loadData">Retry Loading</Button>
    </div>

    <!-- Loading Skeleton -->
    <div v-else-if="loading && !dashboardData" class="space-y-6">
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div v-for="n in 6" :key="n" class="h-28 rounded-xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 h-80 rounded-xl bg-slate-100 dark:bg-slate-900 animate-pulse" />
        <div class="h-80 rounded-xl bg-slate-100 dark:bg-slate-900 animate-pulse" />
      </div>
    </div>

    <!-- Main Dashboard Content -->
    <div v-else-if="dashboardData" class="space-y-6" :class="{ 'opacity-60 transition-opacity': isFetching }">
      <!-- Attention Banner (Critical Issues) -->
      <div
        v-if="totalAttentionItems > 0"
        class="p-4 rounded-xl border border-amber-300 dark:border-amber-900/60 bg-amber-50/90 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
      >
        <div class="flex flex-wrap items-center gap-2">
          <span class="inline-flex items-center gap-1 font-bold text-amber-800 dark:text-amber-300">
            <AlertTriangle class="w-4 h-4 text-amber-600 dark:text-amber-400" />
            {{ totalAttentionItems }} things need attention:
          </span>
          <template v-for="(items, key) in dashboardData.attention" :key="key">
            <span
              v-if="items.length"
              class="px-2 py-0.5 rounded-full font-semibold bg-white dark:bg-slate-900 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800/60"
            >
              {{ items.length }} {{ attentionLabels[key] || key }}
            </span>
          </template>
        </div>

        <router-link
          to="/control-tower"
          class="inline-flex items-center gap-1 font-bold text-brand-600 dark:text-brand-400 hover:underline shrink-0"
        >
          <span>Open Control Tower</span>
          <ArrowRight class="w-3.5 h-3.5" />
        </router-link>
      </div>

      <!-- KPI Row (6 responsive cards) -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <!-- 1. Orders -->
        <KpiCard
          title="Orders"
          :value="dashboardData.kpis.orders.value"
          :delta="dashboardData.kpis.orders.delta_pct"
          subtitle="excl. cancelled"
          :sparkline="ordersSparkline"
          clickable
          @click="drillDown('/r/orders')"
        />

        <!-- 2. Trips Completed -->
        <KpiCard
          title="Trips Done"
          :value="dashboardData.kpis.trips_completed.value"
          :delta="dashboardData.kpis.trips_completed.delta_pct"
          :subtitle="`${dashboardData.fleet.on_trip} on road now`"
          clickable
          @click="drillDown('/r/trips', { status: 'completed' })"
        />

        <!-- 3. On-Time Delivery -->
        <KpiCard
          title="On-Time Delivery"
          :value="`${dashboardData.kpis.on_time_pct.value}%`"
          :delta="calcPtsDelta(dashboardData.kpis.on_time_pct)"
          is-pts
          good-direction="up"
          :subtitle="`${dashboardData.kpis.late_trips.value} late (>15m)`"
          clickable
          @click="drillDown('/r/trips', { status: 'active' })"
        />

        <!-- 4. Revenue -->
        <KpiCard
          title="Revenue"
          :value="compact(dashboardData.kpis.revenue.value, dashboardData.currency)"
          :delta="dashboardData.kpis.revenue.delta_pct"
          good-direction="up"
          :subtitle="`Cost ${compact(dashboardData.kpis.cost.value, dashboardData.currency)}`"
          :sparkline="revenueSparkline"
          clickable
          @click="drillDown('/r/orders')"
        />

        <!-- 5. Gross Margin -->
        <KpiCard
          title="Gross Margin"
          :value="`${dashboardData.kpis.margin_pct.value}%`"
          :delta="calcPtsDelta(dashboardData.kpis.margin_pct)"
          is-pts
          good-direction="up"
          :subtitle="`Coverage on ${dashboardData.kpis.cost_coverage_pct.value ?? '—'}%`"
          clickable
          @click="drillDown('/r/orders')"
        />

        <!-- 6. Fleet Utilisation -->
        <KpiCard
          title="Fleet Utilisation"
          :value="`${dashboardData.kpis.fleet_utilisation_pct.value}%`"
          :delta="calcPtsDelta(dashboardData.kpis.fleet_utilisation_pct)"
          is-pts
          good-direction="up"
          subtitle="Active truck days"
          clickable
          @click="drillDown('/r/vehicles')"
        />
      </div>

      <!-- Charts Row 1: Revenue vs Cost & Execution Funnel -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Revenue, Cost & Orders Series Chart -->
        <Card class="p-5 lg:col-span-2 space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <div>
              <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">
                Revenue, Cost & Orders per Day
              </h3>
              <p class="text-xs text-slate-400">Daily operational financial trends and fulfillment volume</p>
            </div>
            <span class="text-xs font-mono font-medium text-slate-500">Currency: {{ dashboardData.currency }}</span>
          </div>

          <div class="h-72 w-full">
            <Bar :data="chartSeriesData" :options="chartSeriesOptions" />
          </div>
        </Card>

        <!-- Execution Funnel Card -->
        <Card class="p-5 space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <div>
              <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Execution Funnel</h3>
              <p class="text-xs text-slate-400">Order pipeline throughput</p>
            </div>
            <span class="text-xs font-mono font-bold text-brand-600 dark:text-brand-400">
              {{ totalFunnelOrders }} total
            </span>
          </div>

          <div class="space-y-3 pt-1">
            <div
              v-for="step in funnelStages"
              :key="step.key"
              class="space-y-1 cursor-pointer group"
              @click="drillDown('/r/orders', { status: step.key })"
            >
              <div class="flex justify-between text-xs">
                <span class="font-medium text-slate-700 dark:text-slate-300 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                  {{ step.label }}
                </span>
                <span class="font-bold text-slate-900 dark:text-slate-100 font-mono">
                  {{ dashboardData.funnel[step.key] || 0 }}
                </span>
              </div>
              <div class="h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                <div
                  :class="['h-full rounded-full transition-all duration-300', step.barColor]"
                  :style="{ width: `${calcFunnelPct(dashboardData.funnel[step.key])}%` }"
                />
              </div>
            </div>
          </div>

          <div v-if="dashboardData.attention?.stuck_orders?.length" class="pt-2 border-t border-slate-100 dark:border-slate-800">
            <span class="text-xs font-semibold text-amber-600 dark:text-amber-400 flex items-center gap-1">
              <AlertCircle class="w-3.5 h-3.5" />
              {{ dashboardData.attention.stuck_orders.length }} orders stuck >48h
            </span>
          </div>
        </Card>
      </div>

      <!-- Quick Metrics Row: Billing, Commercial, Fleet -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- 1. Billing & Receivables -->
        <Card class="p-5 space-y-3 text-xs">
          <div class="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2.5">
            <Receipt class="w-4 h-4 text-brand-600" />
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Billing & Cash</h3>
          </div>
          <div class="space-y-2.5">
            <div class="flex justify-between items-center">
              <span class="text-slate-500">Unbilled (ready for invoice):</span>
              <span class="font-mono font-bold text-slate-900 dark:text-slate-100">
                {{ compact(dashboardData.finance.unbilled_value, dashboardData.currency) }} ({{ dashboardData.finance.unbilled_orders }})
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-slate-500">Invoiced in period:</span>
              <span class="font-mono font-bold text-slate-900 dark:text-slate-100">
                {{ compact(dashboardData.finance.invoiced_value, dashboardData.currency) }}
              </span>
            </div>
            <div class="flex justify-between items-center pt-1 border-t border-slate-100 dark:border-slate-800">
              <span class="text-slate-500">Overdue receivables:</span>
              <span :class="['font-mono font-bold', dashboardData.finance.overdue_count > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-slate-100']">
                {{ compact(dashboardData.finance.overdue_value, dashboardData.currency) }} ({{ dashboardData.finance.overdue_count }} invoices)
              </span>
            </div>
          </div>
        </Card>

        <!-- 2. Commercial Health -->
        <Card class="p-5 space-y-3 text-xs">
          <div class="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2.5">
            <Handshake class="w-4 h-4 text-brand-600" />
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Commercial Health</h3>
          </div>
          <div class="space-y-2.5">
            <div class="flex justify-between items-center">
              <span class="text-slate-500">Contract coverage of orders:</span>
              <span class="font-mono font-bold text-slate-900 dark:text-slate-100">
                {{ dashboardData.commercial.contract_coverage_pct ?? '—' }}%
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-slate-500">Rate inquiry hit rate:</span>
              <span class="font-mono font-bold text-slate-900 dark:text-slate-100">
                {{ dashboardData.commercial.rate_hit_rate_pct ?? '—' }}%
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-slate-500">Outsourced to market:</span>
              <span class="font-mono font-bold text-slate-900 dark:text-slate-100">
                {{ dashboardData.commercial.outsourced_pct ?? '—' }}%
              </span>
            </div>
          </div>
        </Card>

        <!-- 3. Fleet Live Status -->
        <Card class="p-5 space-y-3 text-xs">
          <div class="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2.5">
            <Truck class="w-4 h-4 text-brand-600" />
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Fleet & Drivers (Live)</h3>
          </div>
          <div class="space-y-2.5">
            <div class="flex justify-between items-center">
              <span class="text-slate-500">Own vehicles total:</span>
              <span class="font-mono font-bold text-slate-900 dark:text-slate-100">
                {{ dashboardData.fleet.own_vehicles }} ({{ dashboardData.fleet.on_trip }} active / {{ dashboardData.fleet.idle }} idle)
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-slate-500">Maintenance & lease:</span>
              <span class="font-mono font-bold text-slate-900 dark:text-slate-100">
                {{ dashboardData.fleet.in_maintenance }} shop / {{ dashboardData.fleet.on_lease }} lease
              </span>
            </div>
            <div class="flex justify-between items-center pt-1 border-t border-slate-100 dark:border-slate-800">
              <span class="text-slate-500">Expiring documents (≤30d):</span>
              <span :class="['font-mono font-bold', dashboardData.fleet.documents_expired > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-slate-100']">
                {{ dashboardData.fleet.documents_expiring_30d }} ({{ dashboardData.fleet.documents_expired }} expired)
              </span>
            </div>
          </div>
        </Card>
      </div>

      <!-- Charts Row 2: Top Customers, Revenue by Job Type, Lane Punctuality -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Top Customers -->
        <Card class="p-5 space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Top Customers by Revenue</h3>
            <span class="text-xs text-slate-400">Volume rank</span>
          </div>

          <div class="space-y-3">
            <div
              v-for="(c, idx) in dashboardData.top_customers"
              :key="c.customer"
              class="space-y-1.5"
            >
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[180px]">
                  {{ idx + 1 }}. {{ c.customer }}
                </span>
                <span class="font-mono font-bold text-slate-900 dark:text-slate-100">
                  {{ compact(c.revenue, dashboardData.currency) }}
                </span>
              </div>
              <div class="h-1.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                <div
                  class="h-full bg-brand-500 rounded-full"
                  :style="{ width: `${calcCustomerPct(c.revenue)}%` }"
                />
              </div>
            </div>
          </div>
        </Card>

        <!-- Revenue by Job Type Donut -->
        <Card class="p-5 space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Revenue by Job Type</h3>
            <span class="text-xs text-slate-400">Product mix</span>
          </div>

          <div class="h-60 w-full">
            <Doughnut :data="chartJobTypeData" :options="{ maintainAspectRatio: false }" />
          </div>
        </Card>

        <!-- Lane Punctuality Table -->
        <Card class="p-5 space-y-4 overflow-x-auto">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Corridor Punctuality</h3>
            <span class="text-xs text-slate-400">Transit lanes</span>
          </div>

          <table class="w-full text-left text-xs">
            <thead class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <tr>
                <th class="pb-2">Lane</th>
                <th class="pb-2 text-center">Trips</th>
                <th class="pb-2 text-center">On-Time</th>
                <th class="pb-2 text-right">Avg Delay</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800/60">
              <tr v-for="l in dashboardData.lanes" :key="l.lane">
                <td class="py-2 font-medium text-slate-800 dark:text-slate-200 truncate max-w-[120px]">{{ l.lane }}</td>
                <td class="py-2 text-center font-mono">{{ l.trips }}</td>
                <td class="py-2 text-center">
                  <span
                    :class="[
                      'px-2 py-0.5 rounded-full text-[10px] font-bold',
                      l.on_time_pct >= 90
                        ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                        : l.on_time_pct >= 75
                          ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
                          : 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300'
                    ]"
                  >
                    {{ l.on_time_pct }}%
                  </span>
                </td>
                <td class="py-2 text-right font-mono">{{ l.avg_delay_min }}m</td>
              </tr>
            </tbody>
          </table>
        </Card>
      </div>

      <!-- Branch Comparison Table -->
      <Card class="p-5 space-y-4 overflow-hidden">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Branch Performance Overview</h3>
            <p class="text-xs text-slate-400">Comparative metrics across operating hubs</p>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead class="bg-slate-50 dark:bg-slate-800/60 text-[11px] font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th class="px-4 py-3">Branch</th>
                <th class="px-4 py-3 text-center">Orders</th>
                <th class="px-4 py-3 text-center">Trips Done</th>
                <th class="px-4 py-3 text-center">On-Time</th>
                <th class="px-4 py-3 text-right">Revenue</th>
                <th class="px-4 py-3 text-right">Cost</th>
                <th class="px-4 py-3 text-center">Margin</th>
                <th class="px-4 py-3 text-center">Utilisation</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800/60">
              <tr
                v-for="b in dashboardData.branches"
                :key="b.branch"
                class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
              >
                <td class="px-4 py-3 font-semibold text-slate-900 dark:text-slate-100">{{ b.branch }}</td>
                <td class="px-4 py-3 text-center font-mono">{{ b.orders }}</td>
                <td class="px-4 py-3 text-center font-mono">{{ b.trips_completed }}</td>
                <td class="px-4 py-3 text-center">
                  <span class="font-semibold text-emerald-600 dark:text-emerald-400">{{ b.on_time_pct }}%</span>
                </td>
                <td class="px-4 py-3 text-right font-mono font-bold text-slate-900 dark:text-slate-100">
                  {{ compact(b.revenue, b.currency) }}
                </td>
                <td class="px-4 py-3 text-right font-mono text-slate-500">
                  {{ compact(b.cost, b.currency) }}
                </td>
                <td class="px-4 py-3 text-center font-mono font-semibold">{{ b.margin_pct }}%</td>
                <td class="px-4 py-3 text-center font-mono">{{ b.fleet_utilisation_pct }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  ArcElement,
  BarController,
  LineController,
} from 'chart.js'
import {
  AlertTriangle,
  AlertCircle,
  ArrowRight,
  Receipt,
  Handshake,
  Truck,
} from 'lucide-vue-next'
import api, { errText } from '../api'
import { formatDate, compact } from '../utils/format'
import { useUrlState } from '../composables/useUrlState'

import Card from '../components/ui/Card.vue'
import Button from '../components/ui/Button.vue'
import Select from '../components/ui/Select.vue'
import DateRangePicker from '../components/ui/DateRangePicker.vue'
import Combobox from '../components/ui/Combobox.vue'
import KpiCard from '../components/ui/KpiCard.vue'

Chart.register(
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  ArcElement,
  BarController,
  LineController
)

const router = useRouter()
const route = useRoute()

// Reactive Filter State
const range = ref('30d')
const from = ref('')
const to = ref('')
const branch = ref(null)
const customer = ref(null)
const jobType = ref('')

// Data & Lifecycle
const dashboardData = ref(null)
const loading = ref(true)
const isFetching = ref(false)
const error = ref('')

// Dropdown options
const branchOptions = ref([])
const customerOptions = ref([])

// URL Synchronization
const urlState = useUrlState({
  range: '30d',
  from: '',
  to: '',
  branch: null,
  customer: null,
  job_type: '',
})

watch(
  urlState.state,
  (s) => {
    if (s.range) range.value = s.range
    if (s.from !== undefined) from.value = s.from
    if (s.to !== undefined) to.value = s.to
    if (s.branch !== undefined) branch.value = s.branch
    if (s.customer !== undefined) customer.value = s.customer
    if (s.job_type !== undefined) jobType.value = s.job_type
  },
  { immediate: true }
)

watch([range, from, to, branch, customer, jobType], () => {
  urlState.state.value = {
    range: range.value !== '30d' ? range.value : undefined,
    from: from.value || undefined,
    to: to.value || undefined,
    branch: branch.value || undefined,
    customer: customer.value || undefined,
    job_type: jobType.value || undefined,
  }
})

const hasActiveFilters = computed(() => {
  return range.value !== '30d' || !!from.value || !!to.value || !!branch.value || !!customer.value || !!jobType.value
})

function setPresetRange(r) {
  range.value = r
  from.value = ''
  to.value = ''
}

function resetFilters() {
  range.value = '30d'
  from.value = ''
  to.value = ''
  branch.value = null
  customer.value = null
  jobType.value = ''
}

function drillDown(targetPath, queryParams = {}) {
  const p = { ...queryParams }
  if (branch.value) p.branch = branch.value
  if (customer.value) p.customer = customer.value
  router.push({ path: targetPath, query: p })
}

const attentionLabels = {
  late: 'late trips',
  no_eta: 'trips without ETA',
  stale: 'stale trips (>3 days)',
  gps_silent: 'GPS silent',
  need_truck_24h: 'need a truck <24h',
  stuck_orders: 'orders stuck >48h',
}

const totalAttentionItems = computed(() => {
  if (!dashboardData.value?.attention) return 0
  return Object.values(dashboardData.value.attention).reduce((acc, list) => acc + (list?.length || 0), 0)
})

// Sparklines
const ordersSparkline = computed(() => {
  if (!dashboardData.value?.series) return []
  return dashboardData.value.series.map((s) => s.orders)
})

const revenueSparkline = computed(() => {
  if (!dashboardData.value?.series) return []
  return dashboardData.value.series.map((s) => s.revenue)
})

function calcPtsDelta(kpiObj) {
  if (!kpiObj || kpiObj.value === null || kpiObj.previous === null) return null
  return Math.round((kpiObj.value - kpiObj.previous) * 10) / 10
}

// Funnel Calculations
const funnelStages = [
  { key: 'pending', label: 'Pending', barColor: 'bg-amber-500' },
  { key: 'confirmed', label: 'Confirmed', barColor: 'bg-sky-500' },
  { key: 'active', label: 'In Transit', barColor: 'bg-brand-500' },
  { key: 'completed', label: 'Delivered', barColor: 'bg-emerald-500' },
  { key: 'ready_for_invoice', label: 'Ready for Invoice', barColor: 'bg-violet-500' },
  { key: 'invoiced', label: 'Invoiced', barColor: 'bg-indigo-500' },
]

const totalFunnelOrders = computed(() => {
  if (!dashboardData.value?.funnel) return 0
  return Object.values(dashboardData.value.funnel).reduce((acc, v) => acc + (v || 0), 0)
})

function calcFunnelPct(val) {
  if (!dashboardData.value?.funnel) return 0
  const max = Math.max(1, ...Object.values(dashboardData.value.funnel))
  return Math.round(((val || 0) / max) * 100)
}

function calcCustomerPct(rev) {
  const max = dashboardData.value?.kpis?.revenue?.value || 1
  return Math.min(100, Math.round(((rev || 0) / max) * 100))
}

// Chart: Series Data
const chartSeriesData = computed(() => {
  const series = dashboardData.value?.series || []
  return {
    labels: series.map((s) => s.date.slice(5)),
    datasets: [
      {
        type: 'bar',
        label: 'Revenue',
        data: series.map((s) => s.revenue),
        backgroundColor: '#4F46E5',
        borderRadius: 4,
        yAxisID: 'y',
      },
      {
        type: 'bar',
        label: 'Cost',
        data: series.map((s) => s.cost),
        backgroundColor: '#F97316',
        borderRadius: 4,
        yAxisID: 'y',
      },
      {
        type: 'line',
        label: 'Orders',
        data: series.map((s) => s.orders),
        borderColor: '#10B981',
        backgroundColor: '#10B981',
        tension: 0.35,
        yAxisID: 'y1',
      },
    ],
  }
})

const chartSeriesOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: 'rgba(150, 150, 150, 0.1)' },
    },
    y1: {
      position: 'right',
      beginAtZero: true,
      grid: { display: false },
    },
  },
}

// Chart: Job Type Donut Data
const chartJobTypeData = computed(() => {
  const jobTypes = dashboardData.value?.by_job_type || []
  return {
    labels: jobTypes.map((j) => `${j.job_type} (${j.orders})`),
    datasets: [
      {
        data: jobTypes.map((j) => j.revenue),
        backgroundColor: ['#4F46E5', '#10B981', '#F59E0B', '#64748B'],
        borderWidth: 0,
      },
    ],
  }
})

// Data Fetching
async function loadData() {
  if (dashboardData.value) {
    isFetching.value = true
  } else {
    loading.value = true
  }
  error.value = ''

  const params = { range: range.value }
  if (from.value && to.value) {
    params.from = from.value
    params.to = to.value
  }
  if (branch.value) params.branch = branch.value
  if (customer.value) params.customer = customer.value
  if (jobType.value) params.job_type = jobType.value

  try {
    const res = await api.get('dashboard/', { params })
    dashboardData.value = res.data
  } catch (e) {
    error.value = errText(e)
  } finally {
    loading.value = false
    isFetching.value = false
  }
}

async function loadFilterOptions() {
  try {
    const [branchesRes, customersRes] = await Promise.all([
      api.get('branches/', { params: { page_size: 200 } }),
      api.get('customers/', { params: { page_size: 200 } }),
    ])
    branchOptions.value = [
      { value: null, label: 'All branches' },
      ...(branchesRes.data.results || []).map((b) => ({ value: b.id, label: b.name })),
    ]
    customerOptions.value = [
      { value: null, label: 'All customers' },
      ...(customersRes.data.results || []).map((c) => ({ value: c.id, label: c.company_name || c.name })),
    ]
  } catch (e) {
    console.warn('Failed to load filter options', e)
  }
}

watch([range, branch, customer, jobType], loadData)
watch([from, to], () => {
  if (from.value && to.value) loadData()
})

onMounted(() => {
  loadFilterOptions()
  loadData()
})
</script>
