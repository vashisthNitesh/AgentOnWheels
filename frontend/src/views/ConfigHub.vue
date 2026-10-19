<template>
  <h1 class="text-2xl font-bold">Configuration hub</h1>
  <p class="mb-4 text-sm text-slate-500">Master data, tax rules, fleet & workshop setup.</p>
  <input v-model="q" class="input mb-4 max-w-sm" placeholder="Search settings…" />
  <div v-if="!items" class="grid gap-3 sm:grid-cols-3"><div v-for="n in 9" :key="n" class="skeleton h-16" /></div>
  <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
    <router-link v-for="i in shown" :key="i.key" :to="'/r/' + i.key" class="card p-4 hover:border-brand-500"><span class="text-lg">⚙️</span> <b>{{ i.title }}</b></router-link>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
const items = ref(null), q = ref('')
onMounted(async () => items.value = (await api.get('meta/')).data.groups.Configuration)
const shown = computed(() => items.value.filter(i => i.title.toLowerCase().includes(q.value.toLowerCase())))
</script>
