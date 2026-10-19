<template>
  <div class="mb-4 flex flex-wrap items-end gap-3">
    <div class="flex-1"><h1 class="text-2xl font-bold">Control tower</h1><p class="text-sm text-slate-500">{{ d ? `Updated ${ago}s ago · refreshes every 30s` : 'Loading live data…' }}</p></div>
    <RefSelect resource="branches" v-model="branch" placeholder="All branches" class="!w-44" /><button class="btn-ghost" @click="load">⟳ Refresh</button>
  </div>
  <div v-if="!d" class="grid gap-3 sm:grid-cols-3 lg:grid-cols-5"><div v-for="n in 5" :key="n" class="skeleton h-24" /><div class="skeleton col-span-full h-80" /></div>
  <template v-else>
    <div class="grid gap-3 sm:grid-cols-3 lg:grid-cols-5">
      <button v-for="t in tiles" :key="t.k" :class="['card p-4 text-left', tab === t.k && 'ring-2 ring-brand-500']" @click="tab = t.k">
        <div class="text-xs uppercase text-slate-500">{{ t.l }}</div><div :class="['text-3xl font-bold', t.warn && d.tiles[t.k] ? 'text-rose-600' : '']">{{ d.tiles[t.k] }}</div><div class="text-xs text-slate-500">{{ t.s }}</div></button>
    </div>
    <div class="mt-4 grid gap-4 lg:grid-cols-3">
      <div class="card lg:col-span-2"><h3 class="border-b p-4 font-semibold">On the road (riskiest first)</h3>
        <div v-if="!list.length" class="p-8 text-center text-slate-500">Nothing here right now ✓</div>
        <div v-for="c in list" :key="c.id" class="flex flex-wrap items-center gap-2 border-b p-3 text-sm last:border-0">
          <router-link :to="'/orders/' + c.order_id" class="font-semibold text-brand-600">{{ c.number }}</router-link>
          <span :class="['chip', risk[c.risk][1]]">{{ risk[c.risk][0] }}</span>
          <span :class="['chip', c.gps === 'ok' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700']">GPS {{ c.gps }}</span>
          <span v-if="c.stale" class="chip bg-rose-100 text-rose-700">Stale > 3 days</span>
          <span class="chip bg-slate-100">{{ c.job_type }}</span><span class="min-w-[12rem] flex-1">{{ c.lane }} · {{ c.customer }}</span>
          <span class="text-slate-500">{{ c.truck || 'No truck' }} {{ c.driver ? '· ' + c.driver : '' }}</span>
          <span class="w-full text-xs text-slate-500 sm:w-auto">ETA {{ c.eta ? fmtDate(c.eta) : 'not reported' }}<span v-if="c.delay_minutes"> · {{ c.delay_minutes }} min late</span></span>
        </div></div>
      <div class="space-y-4">
        <div class="card"><h3 class="border-b p-4 font-semibold">Next 24 hours — departures</h3>
          <div v-for="c in d.departures" :key="c.id" class="flex border-b p-3 text-sm last:border-0"><span class="flex-1">{{ c.number }} · {{ c.lane }}</span><span :class="c.status === 'unassigned' ? 'text-rose-600' : ''">{{ c.truck || 'Needs a truck' }}</span></div>
          <p v-if="!d.departures.length" class="p-4 text-sm text-slate-500">No departures.</p></div>
        <div class="card"><h3 class="border-b p-4 font-semibold">Idle own trucks ({{ d.idle_vehicles.length }})</h3>
          <div v-for="v in d.idle_vehicles" :key="v.id" class="flex border-b px-4 py-2 text-sm last:border-0"><span class="flex-1">{{ v.plate_number }}</span><span class="text-slate-500">{{ v.branch__name }}</span></div></div>
      </div>
    </div>
  </template>
</template>
<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import api from '../api'
import RefSelect from '../components/RefSelect.vue'
import { fmtDate } from '../format'
const d = ref(null), branch = ref(null), tab = ref('on_road'), now = ref(Date.now())
const tiles = [{ k: 'on_road', l: 'On the road', s: 'trips in progress' }, { k: 'at_risk', l: 'At risk', s: 'late, no ETA or ETA past plan', warn: 1 },
  { k: 'need_truck', l: 'Need a truck', s: 'unassigned, leaving <24h', warn: 1 }, { k: 'gps_silent', l: 'GPS silent', s: 'no ping 30+ min', warn: 1 }, { k: 'idle', l: 'Idle own trucks', s: 'active & not on a trip' }]
const risk = { late: ['Late', 'bg-rose-100 text-rose-700'], no_eta: ['No ETA', 'bg-amber-100 text-amber-800'], at_risk: ['At risk', 'bg-amber-100 text-amber-800'], on_track: ['On track', 'bg-emerald-100 text-emerald-700'] }
const list = computed(() => tab.value === 'at_risk' ? d.value.on_road.filter(c => c.risk !== 'on_track') : tab.value === 'gps_silent' ? d.value.on_road.filter(c => c.gps === 'silent') : tab.value === 'need_truck' ? d.value.departures.filter(c => c.status === 'unassigned') : d.value.on_road)
const ago = computed(() => Math.max(0, Math.round((now.value - new Date(d.value.updated_at)) / 1000)))
async function load() { d.value = (await api.get('control-tower/', { params: branch.value ? { branch: branch.value } : {} })).data }
let t1, t2
onMounted(() => { load(); t1 = setInterval(load, 30000); t2 = setInterval(() => now.value = Date.now(), 1000) })
onUnmounted(() => { clearInterval(t1); clearInterval(t2) })
watch(branch, load)
</script>
