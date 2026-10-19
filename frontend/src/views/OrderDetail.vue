<template>
  <div v-if="err" class="card p-6 text-rose-700">{{ err }} <router-link to="/r/orders" class="underline">Back to orders</router-link></div>
  <div v-else-if="!o" class="space-y-3"><div class="skeleton h-8 w-72" /><div class="grid gap-3 lg:grid-cols-3"><div class="skeleton h-60 lg:col-span-2" /><div class="skeleton h-60" /></div></div>
  <div v-else>
    <router-link to="/r/orders" class="text-sm text-brand-600">← Orders</router-link>
    <div class="mb-4 mt-1 flex flex-wrap items-center gap-3">
      <h1 class="text-2xl font-bold">{{ o.number }}</h1>
      <span :class="['chip text-sm', STATUS_COLORS[o.status]]">{{ o.status_label }}</span>
      <span class="chip bg-slate-100">{{ o.job_type }}</span>
      <span class="text-slate-500">{{ o.lane_label }} · {{ o.lane_detail.service_type }}</span>
      <div class="flex-1" />
      <button class="btn-ghost" @click="copy">{{ copied ? 'Copied ✓' : 'Copy order no.' }}</button>
      <button v-for="s in o.next_statuses" :key="s.value" :class="['cancelled', 'rejected'].includes(s.value) ? 'btn-ghost text-rose-600' : 'btn-primary'" :disabled="busy" @click="move(s.value)">→ {{ s.label }}</button>
      <router-link :to="`/r/orders/${o.id}/edit`" class="btn-ghost">Edit</router-link>
    </div>
    <p v-if="msg" class="mb-3 rounded bg-rose-50 p-2 text-sm text-rose-700">{{ msg }}</p>
    <!-- status timeline -->
    <div class="card mb-4 flex flex-wrap gap-1 p-3 text-xs">
      <span v-for="(s, i) in flow" :key="s[0]" :class="['rounded px-2 py-1', idx >= i ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-500']">{{ s[1] }}</span>
    </div>
    <div class="grid gap-4 lg:grid-cols-3">
      <div class="space-y-4 lg:col-span-2">
        <div class="card grid gap-4 p-5 sm:grid-cols-4">
          <Kv l="Customer" :v="o.customer_label" /><Kv l="Branch" :v="o.branch_label" /><Kv l="Order date" :v="fmtDate(o.order_date)" /><Kv l="Loading" :v="fmtDate(o.loading_at)" />
          <Kv l="Sell rate" :v="fmtMoney(o.sell_rate, o.currency)" /><Kv l="Cost (legs)" :v="fmtMoney(o.cost, o.currency)" /><Kv l="Margin" :v="fmtMoney(o.margin, o.currency)" />
          <Kv l="Vehicles committed" :v="`${o.vehicles_committed} of ${o.num_vehicles} · ${o.allocation_status}`" />
        </div>
        <div class="grid gap-4 sm:grid-cols-2">
          <div class="card p-5"><h3 class="mb-2 font-semibold">📍 Pick up — {{ o.lane_detail.source }}</h3><p class="text-sm">{{ o.pickup_address || '—' }}</p><p class="text-sm text-slate-500">{{ o.pickup_contact }}</p><p class="mt-1 text-xs">Load cut-off: {{ fmtDate(o.load_cutoff) }}</p></div>
          <div class="card p-5"><h3 class="mb-2 font-semibold">🏁 Drop — {{ o.lane_detail.destination }}</h3><p class="text-sm">{{ o.drop_address || '—' }}</p><p class="text-sm text-slate-500">{{ o.drop_contact }}</p><p class="mt-1 text-xs">Offload cut-off: {{ fmtDate(o.offload_cutoff) }}</p></div>
        </div>
        <div class="card overflow-x-auto">
          <div class="flex items-center border-b p-4"><h3 class="flex-1 font-semibold">Legs & trips</h3><router-link :to="`/r/trips/new`" class="btn-ghost">＋ Add leg</router-link></div>
          <table class="min-w-full text-sm"><thead class="bg-slate-50"><tr><th class="th">Trip</th><th class="th">Leg</th><th class="th">Status</th><th class="th">Truck</th><th class="th">Driver</th><th class="th">Planned</th><th class="th">Delay</th><th class="th">Buy</th></tr></thead>
            <tbody><tr v-for="t in o.trips" :key="t.id" class="cursor-pointer border-t hover:bg-brand-50" @click="$router.push('/r/trips/' + t.id)">
              <td class="td font-medium">{{ t.number }}</td><td class="td">{{ t.leg_no }}</td><td class="td"><span :class="['chip', STATUS_COLORS[t.status]]">{{ t.status_label }}</span></td>
              <td class="td">{{ t.vehicle_label || (t.vendor_label ? 'Market · ' + t.vendor_label : '—') }}</td><td class="td">{{ t.driver_label || '—' }}</td>
              <td class="td">{{ fmtDate(t.planned_start) }}</td><td class="td">{{ t.delay_minutes ? t.delay_minutes + ' min' : 'On time' }}</td><td class="td">{{ fmtMoney(t.buy_rate, o.currency) }}</td></tr>
              <tr v-if="!o.trips.length"><td colspan="8" class="td text-center text-slate-500">No legs yet — confirming the order creates one leg per vehicle.</td></tr></tbody></table>
        </div>
      </div>
      <div class="space-y-4">
        <div class="card p-5 text-sm"><h3 class="mb-2 font-semibold">Cargo</h3>
          <Kv l="Product" :v="o.product_label" /><Kv l="Container" :v="o.container_type_label" /><Kv l="Commodity" :v="o.commodity" /><Kv l="Weight" :v="o.weight_t + ' t'" /><Kv l="Quantity" :v="o.quantity" />
          <p class="mt-2 flex gap-1"><span v-if="o.temperature_controlled" class="chip bg-sky-100">❄ Temp</span><span v-if="o.hazardous" class="chip bg-rose-100">☣ Hazardous</span><span v-if="o.stackable" class="chip bg-slate-100">Stackable</span></p></div>
        <div class="card p-5 text-sm"><h3 class="mb-2 font-semibold">Commercial</h3><Kv l="Reference" :v="o.reference" /><Kv l="Shipment ref" :v="o.shipment_reference" /><Kv l="Contract" :v="o.contract_label || 'No active contract ⚠'" /><Kv l="Vendor" :v="o.vendor_label" />
          <div v-for="i in o.invoices" :key="i.id"><router-link :to="'/r/invoices/' + i.id" class="text-brand-600">🧾 {{ i.number }} ({{ i.status }})</router-link></div></div>
        <div class="card p-5 text-sm"><h3 class="mb-2 font-semibold">Audit</h3><Kv l="Created" :v="fmtDate(o.created_at) + ' by ' + (o.created_by || '—')" /><Kv l="Updated" :v="fmtDate(o.updated_at)" /><p v-if="o.notes" class="mt-2">{{ o.notes }}</p></div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRoute } from 'vue-router'
import api, { errText } from '../api'
import { fmtDate, fmtMoney, STATUS_COLORS } from '../format'
const Kv = (p) => h('div', { class: 'mb-1' }, [h('div', { class: 'text-xs text-slate-500' }, p.l), h('div', { class: 'font-medium' }, p.v ?? '—')])
Kv.props = ['l', 'v']
const route = useRoute(), o = ref(null), err = ref(''), msg = ref(''), busy = ref(false), copied = ref(false)
const flow = [['pending', 'Pending'], ['confirmed', 'Confirmed'], ['active', 'Active'], ['completed', 'Completed'], ['ready_for_invoice', 'Ready for invoice'], ['invoiced', 'Invoice generated']]
const idx = computed(() => flow.findIndex(f => f[0] === o.value.status))
async function load() { try { o.value = (await api.get(`orders/${route.params.id}/full/`)).data } catch (e) { err.value = e.response?.status === 404 ? 'Order not found.' : errText(e) } }
async function move(s) { busy.value = true; msg.value = ''; try { o.value = (await api.post(`orders/${o.value.id}/transition/`, { status: s })).data } catch (e) { msg.value = errText(e) } finally { busy.value = false } }
function copy() { navigator.clipboard?.writeText(o.value.number); copied.value = true; setTimeout(() => copied.value = false, 1500) }
onMounted(load)
</script>
