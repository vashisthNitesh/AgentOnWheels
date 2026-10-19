<template>
  <div v-if="!meta" class="space-y-3"><div class="skeleton h-8 w-60" /><div class="skeleton h-10" /><div class="skeleton h-96" /></div>
  <div v-else>
    <div class="mb-4 flex flex-wrap items-end gap-3">
      <div class="flex-1"><h1 class="text-2xl font-bold">{{ meta.icon }} {{ meta.title }}</h1>
        <p class="text-sm text-slate-500">{{ loading ? 'Loading…' : `${total} record${total === 1 ? '' : 's'}` }}<span v-if="meta.key === 'trips'"> · counts are per leg</span></p></div>
      <button class="btn-ghost" :disabled="exporting" @click="exportCsv">{{ exporting ? 'Exporting…' : '⬇ Export CSV' }}</button>
      <router-link v-if="meta.create" :to="`/r/${meta.key}/new`" class="btn-primary">＋ New</router-link>
    </div>

    <div class="card mb-3 p-3">
      <div class="flex flex-wrap gap-2">
        <input v-if="meta.search" v-model="search" class="input max-w-xs" placeholder="Search…" />
        <template v-for="f in visibleFilters" :key="f.name">
          <RefSelect v-if="f.type === 'fk'" :resource="f.resource" v-model="filters[f.name]" :placeholder="plural(f.label)" class="!w-48" />
          <select v-else-if="f.type === 'choice'" v-model="filters[f.name]" class="input !w-44"><option :value="undefined">{{ plural(f.label) }}</option><option v-for="c in f.choices" :key="c.value" :value="c.value">{{ c.label }}</option></select>
          <select v-else-if="f.type === 'bool'" v-model="filters[f.name]" class="input !w-40"><option :value="undefined">{{ f.label }}: any</option><option value="true">{{ f.label }}: yes</option><option value="false">{{ f.label }}: no</option></select>
        </template>
        <template v-for="d in meta.dates" :key="d.name">
          <label class="flex items-center gap-1 text-xs text-slate-500">{{ d.label }}
            <input type="date" v-model="dates[d.name + '_from']" class="input !w-36" /> – <input type="date" v-model="dates[d.name + '_to']" class="input !w-36" /></label>
        </template>
        <button v-if="meta.filters.length > 4" class="btn-ghost" @click="more = !more">{{ more ? 'Fewer filters' : 'More filters' }}</button>
        <button v-if="activeFilters" class="btn-ghost text-rose-600" @click="clearAll">Clear filters ({{ activeFilters }})</button>
        <div class="flex-1" />
        <div class="relative"><button class="btn-ghost" @click="showCols = !showCols">▦ Columns</button>
          <div v-if="showCols" class="card absolute right-0 z-20 mt-1 max-h-80 w-56 overflow-auto p-2">
            <label v-for="c in meta.columns" :key="c" class="flex items-center gap-2 px-1 py-0.5 text-sm"><input type="checkbox" :checked="!hidden.includes(c)" @change="toggleCol(c)" />{{ label(c) }}</label>
          </div></div>
        <button class="btn-ghost" title="Refresh" @click="load">⟳</button>
      </div>
      <div v-if="meta.status_choices" class="mt-3 flex flex-wrap gap-1 border-t pt-3">
        <button v-for="t in tabs" :key="t.value" :class="['rounded-full px-3 py-1 text-sm', status === t.value ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200']" @click="status = t.value">
          {{ t.label }} <span class="ml-1 opacity-70">{{ counts ? (counts[t.value] || 0) : '·' }}</span></button>
      </div>
    </div>

    <p v-if="error" class="mb-3 rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{{ error }} <button class="underline" @click="load">Retry</button></p>
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200">
          <thead class="sticky top-0 bg-slate-50"><tr>
            <th v-for="c in cols" :key="c" class="th cursor-pointer select-none" @click="sortBy(c)">{{ label(c) }} <span v-if="ordering === c">▲</span><span v-else-if="ordering === '-' + c">▼</span></th>
          </tr></thead>
          <tbody class="divide-y divide-slate-100">
            <template v-if="loading"><tr v-for="n in 8" :key="n"><td v-for="c in cols" :key="c" class="td"><div class="skeleton h-4 w-20" /></td></tr></template>
            <tr v-else v-for="r in rows" :key="r.id" class="cursor-pointer hover:bg-brand-50" @click="open(r)">
              <td v-for="c in cols" :key="c" class="td"><Cell :row="r" :name="c" :f="meta.fields[c]" /></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!loading && !rows.length" class="p-10 text-center text-slate-500">
        <p class="text-3xl">🗂️</p><p class="mt-2 font-medium">No {{ meta.title.toLowerCase() }} {{ activeFilters || status !== 'all' || search ? 'match these filters' : 'yet' }}</p>
        <router-link v-if="meta.create && !activeFilters" :to="`/r/${meta.key}/new`" class="btn-primary mt-3">Create the first one</router-link>
      </div>
      <div class="flex flex-wrap items-center gap-3 border-t px-3 py-2 text-sm text-slate-600">
        Rows <select v-model.number="pageSize" class="input !w-20 !py-1"><option>20</option><option>50</option><option>100</option></select>
        <span class="flex-1">{{ total ? `${(page - 1) * pageSize + 1}–${Math.min(page * pageSize, total)} of ${total}` : '0 records' }}</span>
        <button class="btn-ghost !py-1" :disabled="page === 1" @click="page = 1">«</button><button class="btn-ghost !py-1" :disabled="page === 1" @click="page--">‹</button>
        <button class="btn-ghost !py-1" :disabled="page >= pages" @click="page++">›</button><button class="btn-ghost !py-1" :disabled="page >= pages" @click="page = pages">»</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { errText } from '../api'
import Cell from '../components/Cell.vue'
import RefSelect from '../components/RefSelect.vue'
const route = useRoute(), router = useRouter()
const key = route.params.key
const meta = ref(null), rows = ref([]), total = ref(0), counts = ref(null), loading = ref(true), error = ref(''), exporting = ref(false)
const search = ref(route.query.search || ''), status = ref(route.query.status || 'all'), page = ref(1), pageSize = ref(20), ordering = ref('')
const filters = reactive({}), dates = reactive({}), more = ref(false), showCols = ref(false)
const hidden = ref(JSON.parse(localStorage.getItem('cols_' + key) || 'null') || [])
const plural = l => 'All ' + (l.toLowerCase().replace(/y$/, 'ie').replace(/(s|ch)$/, '$1e') + 's').replace(/statuss$/, 'statuses')
const label = c => meta.value.fields[c]?.label || c.replace(/_/g, ' ').replace(/^./, s => s.toUpperCase())
const cols = computed(() => meta.value.columns.filter(c => !hidden.value.includes(c)))
const visibleFilters = computed(() => more.value ? meta.value.filters : meta.value.filters.slice(0, 4))
const tabs = computed(() => [{ value: 'all', label: 'All' }, ...meta.value.status_choices])
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const activeFilters = computed(() => Object.values(filters).filter(v => v !== undefined && v !== null && v !== '').length + Object.values(dates).filter(Boolean).length)
function toggleCol(c) { hidden.value = hidden.value.includes(c) ? hidden.value.filter(x => x !== c) : [...hidden.value, c]; localStorage.setItem('cols_' + key, JSON.stringify(hidden.value)) }
function clearAll() { Object.keys(filters).forEach(k => delete filters[k]); Object.keys(dates).forEach(k => delete dates[k]); search.value = '' }
function sortBy(c) { if (meta.value.fields[c]?.type === 'computed') return; ordering.value = ordering.value === c ? '-' + c : ordering.value === '-' + c ? '' : c }
function params(withStatus = true) {
  const p = { page: page.value, page_size: pageSize.value }
  if (search.value) p.search = search.value
  if (ordering.value) p.ordering = ordering.value
  for (const [k, v] of Object.entries(filters)) if (v !== undefined && v !== null && v !== '') p[k] = v
  for (const d of meta.value.dates) {
    const dt = meta.value.fields[d.name].type === 'datetime' ? '__date' : ''
    if (dates[d.name + '_from']) p[`${d.name}${dt}__gte`] = dates[d.name + '_from']
    if (dates[d.name + '_to']) p[`${d.name}${dt}__lte`] = dates[d.name + '_to']
  }
  if (withStatus && meta.value.status && status.value !== 'all') p[meta.value.status] = status.value
  return p
}
let seq = 0
async function load() {
  const my = ++seq; loading.value = true; error.value = ''
  try {
    const [l, c] = await Promise.all([api.get(key + '/', { params: params() }), meta.value.status ? api.get(key + '/counts/', { params: params(false) }) : Promise.resolve(null)])
    if (my !== seq) return
    rows.value = l.data.results; total.value = l.data.count; counts.value = c?.data || null
  } catch (e) { if (my === seq) error.value = errText(e) } finally { if (my === seq) loading.value = false }
}
async function exportCsv() {
  exporting.value = true
  try {
    const p = params(); delete p.page; delete p.page_size
    const r = await api.get(key + '/export/', { params: p, responseType: 'blob' })
    const a = document.createElement('a'); a.href = URL.createObjectURL(r.data); a.download = `${key}.csv`; a.click()
  } catch (e) { error.value = errText(e) } finally { exporting.value = false }
}
function open(r) { router.push(key === 'orders' ? `/orders/${r.id}` : `/r/${key}/${r.id}`) }
let timer
watch(search, () => { clearTimeout(timer); timer = setTimeout(() => { page.value = 1; load() }, 300) })
watch([status, pageSize, ordering, () => ({ ...filters }), () => ({ ...dates })], () => { page.value = 1; load() }, { deep: true })
watch(page, load)
onMounted(async () => {
  try { meta.value = (await api.get('meta/' + key + '/')).data } catch (e) { error.value = errText(e); return }
  for (const [k, v] of Object.entries(route.query)) if (meta.value.filters.some(f => f.name === k)) filters[k] = isNaN(v) ? v : Number(v)
  load()
})
</script>
