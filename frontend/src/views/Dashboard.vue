<template>
  <div class="mb-4 flex flex-wrap items-end gap-3">
    <div class="flex-1"><h1 class="text-2xl font-bold">Dashboard</h1>
      <p class="text-sm text-slate-500" v-if="d">{{ fmtDate(d.period.start) }} – {{ fmtDate(d.period.end) }} · vs {{ fmtDate(d.period.prev_start) }} – {{ fmtDate(d.period.prev_end) }}</p></div>
    <RefSelect resource="branches" v-model="branch" placeholder="All branches" class="!w-44" />
    <RefSelect resource="customers" v-model="customer" placeholder="All customers" class="!w-48" />
    <select v-model="jobType" class="input !w-36"><option value="">All job types</option><option>FTL</option><option>LTL</option><option>FCL</option></select>
    <div class="flex overflow-hidden rounded-lg border bg-white">
      <button v-for="r in ['7d', '30d', '90d', 'mtd']" :key="r" :class="['px-3 py-2 text-sm', range === r ? 'bg-brand-600 text-white' : 'hover:bg-slate-50']" @click="range = r; from = to = ''">{{ r.toUpperCase() }}</button>
    </div>
    <input type="date" v-model="from" class="input !w-36" /><input type="date" v-model="to" class="input !w-36" />
  </div>
  <p v-if="error" class="mb-3 rounded bg-rose-50 p-3 text-sm text-rose-700">{{ error }} <button class="underline" @click="load">Retry</button></p>
  <div v-if="!d" class="grid gap-3 sm:grid-cols-3 lg:grid-cols-6"><div v-for="n in 6" :key="n" class="skeleton h-28" /><div class="skeleton col-span-full h-72" /></div>
  <div v-else :class="{ 'opacity-60 transition': loading }">
    <div v-if="attnCount" class="card mb-4 flex flex-wrap items-center gap-2 border-amber-300 bg-amber-50 p-3 text-sm">
      <b>⚠ {{ attnCount }} things need attention:</b>
      <span v-for="(v, k) in d.attention" :key="k" v-show="v.length" class="chip bg-white text-amber-800">{{ v.length }} {{ attnLabels[k] }}</span>
      <router-link to="/control-tower" class="ml-auto text-brand-600">Open control tower →</router-link>
    </div>
    <div class="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
      <Kpi t="Orders" :k="d.kpis.orders" sub="excl. cancelled/rejected" />
      <Kpi t="Trips completed" :k="d.kpis.trips_completed" :sub="`${d.fleet.on_trip} own trucks on the road now`" />
      <Kpi t="On time delivery" :k="d.kpis.on_time_pct" suffix="%" pts :sub="`${d.kpis.late_trips.value} late (>15 min)`" />
      <Kpi t="Revenue" :k="d.kpis.revenue" money :cur="d.currency" :sub="`Cost ${compact(d.kpis.cost.value, d.currency)}`" />
      <Kpi t="Gross margin" :k="d.kpis.margin_pct" suffix="%" pts :sub="`Cost captured on ${d.kpis.cost_coverage_pct.value ?? '—'}% of legs`" />
      <Kpi t="Fleet utilisation" :k="d.kpis.fleet_utilisation_pct" suffix="%" pts sub="own vehicle-days with a trip" />
    </div>
    <div class="mt-4 grid gap-4 lg:grid-cols-3">
      <div class="card p-4 lg:col-span-2"><div class="mb-2 flex items-center"><h3 class="flex-1 font-semibold">Revenue, cost & orders per day</h3></div>
        <div class="h-72"><Bar :data="seriesChart" :options="barOpts" /></div></div>
      <div class="card p-4"><h3 class="mb-2 font-semibold">Execution funnel</h3>
        <div v-for="s in funnelSteps" :key="s[0]" class="mb-2"><div class="flex text-sm"><span class="flex-1">{{ s[1] }}</span><b>{{ d.funnel[s[0]] || 0 }}</b></div>
          <div class="h-2 rounded bg-slate-100"><div class="h-2 rounded bg-brand-500" :style="{ width: pct(d.funnel[s[0]] || 0, maxFunnel) + '%' }" /></div></div>
        <p v-if="d.attention.stuck_orders.length" class="mt-2 text-xs text-amber-700">{{ d.attention.stuck_orders.length }} orders not moving for 48h+</p></div>
    </div>
    <div class="mt-4 grid gap-4 lg:grid-cols-3">
      <div class="card p-4"><h3 class="mb-2 font-semibold">💰 Billing & cash</h3>
        <Row l="Unbilled (completed / ready)" :v="`${compact(d.finance.unbilled_value, d.currency)} · ${d.finance.unbilled_orders} orders`" />
        <Row l="Invoiced in period" :v="compact(d.finance.invoiced_value, d.currency)" />
        <Row l="Overdue" :v="`${compact(d.finance.overdue_value, d.currency)} · ${d.finance.overdue_count} invoices`" :warn="d.finance.overdue_count > 0" /></div>
      <div class="card p-4"><h3 class="mb-2 font-semibold">🤝 Commercial health</h3>
        <Row l="Contract coverage of orders" :v="p(d.commercial.contract_coverage_pct)" /><Row l="Rate-inquiry hit rate" :v="p(d.commercial.rate_hit_rate_pct)" />
        <Row l="Vendor bid response rate" :v="p(d.commercial.bid_response_rate_pct)" /><Row l="Trips outsourced to market" :v="p(d.commercial.outsourced_pct)" />
        <Row l="Confirmed without a truck" :v="d.commercial.confirmed_without_truck" :warn="d.commercial.confirmed_without_truck > 0" /></div>
      <div class="card p-4"><h3 class="mb-2 font-semibold">🚛 Fleet (live)</h3>
        <Row l="Own vehicles" :v="d.fleet.own_vehicles" /><Row l="On a trip / idle" :v="`${d.fleet.on_trip} / ${d.fleet.idle}`" /><Row l="In maintenance" :v="d.fleet.in_maintenance" /><Row l="On lease" :v="d.fleet.on_lease" />
        <Row l="Drivers active / present today" :v="`${d.fleet.drivers_active} / ${d.fleet.drivers_present_today}`" />
        <Row l="Documents expiring ≤30d / expired" :v="`${d.fleet.documents_expiring_30d} / ${d.fleet.documents_expired}`" :warn="d.fleet.documents_expired > 0" /></div>
    </div>
    <div class="mt-4 grid gap-4 lg:grid-cols-3">
      <div class="card p-4"><h3 class="mb-2 font-semibold">Top customers by revenue</h3>
        <div v-for="c in d.top_customers" :key="c.customer" class="mb-2 text-sm"><div class="flex"><span class="flex-1 truncate">{{ c.customer }}</span><b>{{ compact(c.revenue, d.currency) }}</b></div>
          <div class="h-1.5 rounded bg-slate-100"><div class="h-1.5 rounded bg-emerald-500" :style="{ width: pct(c.revenue, d.kpis.revenue.value) + '%' }" /></div></div></div>
      <div class="card p-4"><h3 class="mb-2 font-semibold">Revenue by job type</h3><div class="h-56"><Doughnut :data="jobChart" :options="{ maintainAspectRatio: false }" /></div></div>
      <div class="card overflow-x-auto p-4"><h3 class="mb-2 font-semibold">Where punctuality slips (lanes)</h3>
        <table class="w-full text-sm"><tr class="text-xs text-slate-500"><th class="text-left">Lane</th><th>Trips</th><th>On time</th><th>Avg delay</th></tr>
          <tr v-for="l in d.lanes" :key="l.lane" class="border-t"><td class="py-1">{{ l.lane }}</td><td class="text-center">{{ l.trips }}</td>
            <td class="text-center"><span :class="['chip', l.on_time_pct >= 90 ? 'bg-emerald-100' : l.on_time_pct >= 70 ? 'bg-amber-100' : 'bg-rose-100']">{{ l.on_time_pct }}%</span></td><td class="text-center">{{ l.avg_delay_min }}m</td></tr></table></div>
    </div>
    <div class="card mt-4 overflow-x-auto p-4"><h3 class="mb-2 font-semibold">Branches</h3>
      <table class="min-w-full text-sm"><tr><th class="th">Branch</th><th class="th">Orders</th><th class="th">Trips done</th><th class="th">On time</th><th class="th">Revenue</th><th class="th">Cost</th><th class="th">Margin</th><th class="th">Utilisation</th></tr>
        <tr v-for="b in d.branches" :key="b.branch" class="border-t"><td class="td">{{ b.branch }}</td><td class="td">{{ b.orders }}</td><td class="td">{{ b.trips_completed }}</td><td class="td">{{ p(b.on_time_pct) }}</td>
          <td class="td">{{ compact(b.revenue, b.currency) }}</td><td class="td">{{ compact(b.cost, b.currency) }}</td><td class="td">{{ p(b.margin_pct) }}</td><td class="td">{{ p(b.fleet_utilisation_pct) }}</td></tr></table></div>
  </div>
</template>
<script setup>
import { ref, computed, watch, onMounted, h } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import { Chart, BarElement, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend, ArcElement, BarController, LineController } from 'chart.js'
import api, { errText } from '../api'
import RefSelect from '../components/RefSelect.vue'
import { fmtDate, compact } from '../format'
Chart.register(BarElement, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend, ArcElement, BarController, LineController)
const d = ref(null), loading = ref(false), error = ref('')
const range = ref('30d'), from = ref(''), to = ref(''), branch = ref(null), customer = ref(null), jobType = ref('')
const p = v => v === null || v === undefined ? '—' : v + '%'
const pct = (a, b) => b ? Math.min(100, Math.round(100 * a / b)) : 0
const attnLabels = { late: 'late trips', no_eta: 'trips without ETA', stale: 'stale trips (>3 days)', gps_silent: 'GPS silent', need_truck_24h: 'need a truck <24h', stuck_orders: 'orders stuck 48h+' }
const attnCount = computed(() => Object.values(d.value?.attention || {}).reduce((s, v) => s + v.length, 0))
const funnelSteps = [['pending', 'Pending'], ['confirmed', 'Confirmed'], ['active', 'Active'], ['completed', 'Completed'], ['ready_for_invoice', 'Ready for invoice'], ['invoiced', 'Invoiced']]
const maxFunnel = computed(() => Math.max(1, ...Object.values(d.value.funnel)))
const seriesChart = computed(() => ({ labels: d.value.series.map(s => s.date.slice(5)), datasets: [
  { type: 'bar', label: 'Revenue', data: d.value.series.map(s => s.revenue), backgroundColor: '#3b82f6', yAxisID: 'y' },
  { type: 'bar', label: 'Cost', data: d.value.series.map(s => s.cost), backgroundColor: '#f97316', yAxisID: 'y' },
  { type: 'line', label: 'Orders', data: d.value.series.map(s => s.orders), borderColor: '#10b981', yAxisID: 'y1', tension: .3 }] }))
const barOpts = { maintainAspectRatio: false, scales: { y: { beginAtZero: true }, y1: { position: 'right', beginAtZero: true, grid: { display: false } } } }
const jobChart = computed(() => ({ labels: d.value.by_job_type.map(j => `${j.job_type} (${j.orders})`), datasets: [{ data: d.value.by_job_type.map(j => j.revenue), backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'] }] }))
const Kpi = (pr) => {
  const k = pr.k, v = k.value
  const delta = pr.pts ? (v !== null && k.previous !== null ? Math.round((v - k.previous) * 10) / 10 : null) : k.delta_pct
  return h('div', { class: 'card p-4' }, [h('div', { class: 'text-xs font-medium uppercase text-slate-500' }, pr.t),
    h('div', { class: 'mt-1 text-2xl font-bold' }, v === null ? '—' : pr.money ? compact(v, pr.cur) : v + (pr.suffix || '')),
    h('div', { class: ['text-xs', delta > 0 ? 'text-emerald-600' : delta < 0 ? 'text-rose-600' : 'text-slate-400'] }, delta === null ? 'no prior data' : `${delta > 0 ? '▲' : delta < 0 ? '▼' : '■'} ${Math.abs(delta)}${pr.pts ? ' pts' : '%'} vs prev`),
    h('div', { class: 'mt-1 text-xs text-slate-500' }, pr.sub)])
}
Kpi.props = { t: String, k: Object, sub: String, suffix: String, money: Boolean, cur: String, pts: Boolean }
const Row = (pr) => h('div', { class: 'flex border-b py-1.5 text-sm last:border-0' }, [h('span', { class: 'flex-1 text-slate-600' }, pr.l), h('b', { class: pr.warn ? 'text-rose-600' : '' }, String(pr.v ?? '—'))])
Row.props = ['l', 'v', 'warn']
async function load() {
  loading.value = true; error.value = ''
  const params = { range: range.value }
  if (from.value && to.value) { params.from = from.value; params.to = to.value }
  if (branch.value) params.branch = branch.value
  if (customer.value) params.customer = customer.value
  if (jobType.value) params.job_type = jobType.value
  try { d.value = (await api.get('dashboard/', { params })).data } catch (e) { error.value = errText(e) } finally { loading.value = false }
}
watch([range, branch, customer, jobType], load); watch([from, to], () => { if (from.value && to.value) load() })
onMounted(load)
</script>
