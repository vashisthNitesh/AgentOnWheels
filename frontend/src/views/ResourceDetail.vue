<template>
  <div v-if="err" class="card p-6 text-rose-700">{{ err }}</div>
  <div v-else-if="!rec" class="space-y-3"><div class="skeleton h-8 w-60" /><div class="skeleton h-80" /></div>
  <div v-else class="mx-auto max-w-5xl">
    <router-link :to="`/r/${key}`" class="text-sm text-brand-600">← {{ meta.title }}</router-link>
    <div class="mb-4 mt-1 flex flex-wrap items-center gap-3">
      <h1 class="flex-1 text-2xl font-bold">{{ rec.display }}</h1>
      <span v-if="meta.status" :class="['chip text-sm', STATUS_COLORS[rec[meta.status]]]">{{ rec[meta.status + '_label'] }}</span>
      <button v-if="key === 'drivers'" class="btn-ghost" @click="setPass">🔒 Set app passcode</button>
      <a v-if="key === 'reports'" class="btn-ghost" href="#" @click.prevent="dl">⬇ Download CSV</a>
      <router-link :to="`/r/${key}/${id}/edit`" class="btn-primary">Edit</router-link>
      <button class="btn-ghost text-rose-600" @click="del">Delete</button>
    </div>
    <p v-if="msg" class="mb-3 rounded bg-emerald-50 p-2 text-sm text-emerald-700">{{ msg }}</p>
    <div class="card grid gap-x-8 gap-y-3 p-5 text-sm sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="f in Object.values(meta.fields)" :key="f.name"><div class="text-xs text-slate-500">{{ f.label }}</div><div class="font-medium"><Cell :row="rec" :name="f.name" :f="f" /></div></div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { errText } from '../api'
import Cell from '../components/Cell.vue'
import { STATUS_COLORS } from '../format'
const route = useRoute(), router = useRouter(), key = route.params.key, id = route.params.id
const rec = ref(null), meta = ref(null), err = ref(''), msg = ref('')
async function load() { try { [meta.value, rec.value] = (await Promise.all([api.get(`meta/${key}/`), api.get(`${key}/${id}/`)])).map(r => r.data) } catch (e) { err.value = errText(e) } }
async function del() { if (!confirm('Delete this record? This cannot be undone.')) return; try { await api.delete(`${key}/${id}/`); router.push(`/r/${key}`) } catch (e) { alert(errText(e)) } }
async function setPass() {
  const p = prompt('New 6+ digit passcode for the driver app (stored hashed, never shown again):'); if (!p) return
  try { await api.post(`drivers/${id}/set_passcode/`, { passcode: p }); msg.value = 'Passcode updated.'; load() } catch (e) { alert(errText(e)) }
}
async function dl() { const r = await api.get(`reports/${id}/download/`, { responseType: 'blob' }); const a = document.createElement('a'); a.href = URL.createObjectURL(r.data); a.download = rec.value.number + '.csv'; a.click() }
onMounted(load)
</script>
