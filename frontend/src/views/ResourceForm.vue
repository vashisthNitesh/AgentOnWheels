<template>
  <div v-if="!meta || loadingRec" class="space-y-3"><div class="skeleton h-8 w-60" /><div class="skeleton h-96" /></div>
  <div v-else class="mx-auto max-w-4xl">
    <router-link :to="back" class="text-sm text-brand-600">← Back</router-link>
    <h1 class="mb-4 text-2xl font-bold">{{ id ? 'Edit' : 'New' }} {{ meta.title.replace(/s$/, '').toLowerCase() }}</h1>
    <div v-if="steps.length > 1" class="mb-4 flex flex-wrap gap-2">
      <button v-for="(s, i) in steps" :key="i" :class="['flex items-center gap-2 rounded-full px-3 py-1 text-sm', i === step ? 'bg-brand-600 text-white' : stepErrors(i).length ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-700']" @click="step = i">
        <span class="font-bold">{{ i + 1 }}</span>{{ s.title }}<span v-if="stepErrors(i).length">⚠</span></button>
    </div>
    <form class="card p-5" @submit.prevent="next">
      <div v-if="step < steps.length" class="grid gap-4 sm:grid-cols-2">
        <FieldInput v-for="f in steps[step].fields" :key="f" :f="meta.fields[f]" v-model="data[f]" :error="errors[f]" />
      </div>
      <div v-else>
        <h2 class="mb-3 font-semibold">Review</h2>
        <dl class="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
          <template v-for="f in editable" :key="f"><dt class="text-slate-500">{{ meta.fields[f].label }}</dt><dd>{{ data[f] === undefined || data[f] === null || data[f] === '' ? '—' : String(data[f]) }}</dd></template>
        </dl>
      </div>
      <div v-if="missing.length" class="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">To continue, fill in: <b>{{ missing.map(f => meta.fields[f].label).join(', ') }}</b></div>
      <p v-if="errors.non_field_errors" class="mt-4 rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{{ errors.non_field_errors }}</p>
      <div class="mt-6 flex justify-between">
        <button type="button" class="btn-ghost" @click="step > 0 ? step-- : $router.push(back)">{{ step > 0 ? '‹ Back' : 'Cancel' }}</button>
        <button class="btn-primary" :disabled="saving">{{ saving ? 'Saving…' : step < steps.length ? 'Next ›' : (id ? 'Save changes' : 'Create') }}</button>
      </div>
    </form>
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import FieldInput from '../components/FieldInput.vue'
const route = useRoute(), router = useRouter()
const key = route.params.key, id = route.params.id
const meta = ref(null), data = reactive({}), errors = ref({}), step = ref(0), saving = ref(false), loadingRec = ref(!!id), tried = ref(false)
const back = computed(() => id ? (key === 'orders' ? `/orders/${id}` : `/r/${key}/${id}`) : `/r/${key}`)
const editable = computed(() => Object.values(meta.value.fields).filter(f => !f.readonly && f.type !== 'computed').map(f => f.name))
const steps = computed(() => {
  if (meta.value.steps) {
    const s = meta.value.steps.map(x => ({ title: x.title, fields: x.fields.filter(f => editable.value.includes(f)) }))
    const rest = editable.value.filter(f => !s.some(x => x.fields.includes(f)))
    if (rest.length) s.push({ title: 'Other', fields: rest })
    return s
  }
  return [{ title: 'Details', fields: editable.value }]
})
const empty = v => v === undefined || v === null || v === '' || (Array.isArray(v) && !v.length)
const missingIn = i => (steps.value[i]?.fields || []).filter(f => meta.value.fields[f].required && empty(data[f]))
const missing = computed(() => tried.value ? (step.value < steps.value.length ? missingIn(step.value) : steps.value.flatMap((_, i) => missingIn(i))) : [])
const stepErrors = i => steps.value[i].fields.filter(f => errors.value[f])
async function next() {
  tried.value = true
  if (step.value < steps.value.length) {
    if (missingIn(step.value).length) return
    tried.value = false; step.value++; return
  }
  saving.value = true; errors.value = {}
  const body = Object.fromEntries(editable.value.filter(f => data[f] !== undefined).map(f => [f, data[f] === '' ? null : data[f]]))
  try {
    const r = id ? await api.patch(`${key}/${id}/`, body) : await api.post(key + '/', body)
    router.push(key === 'orders' ? `/orders/${r.data.id}` : `/r/${key}/${r.data.id}`)
  } catch (e) {
    const d = e.response?.data || {}
    errors.value = Object.fromEntries(Object.entries(d).map(([k, v]) => [k, [].concat(v).join(' ')]))
    if (!e.response) errors.value = { non_field_errors: 'Network error — nothing was saved. Retry.' }
    const bad = steps.value.findIndex((_, i) => stepErrors(i).length)
    if (bad >= 0) step.value = bad
    else if (!errors.value.non_field_errors) errors.value.non_field_errors = Object.values(errors.value).join(' ')
  } finally { saving.value = false }
}
onMounted(async () => {
  meta.value = (await api.get('meta/' + key + '/')).data
  if (id) { const r = (await api.get(`${key}/${id}/`)).data; editable.value.forEach(f => data[f] = r[f]); loadingRec.value = false }
  else { for (const f of editable.value) if (meta.value.fields[f].type === 'bool') data[f] = false
    if (data.order_date === undefined && meta.value.fields.order_date) data.order_date = new Date().toISOString().slice(0, 10) }
})
</script>
