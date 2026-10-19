<template>
  <router-view v-if="$route.meta.public" />
  <div v-else class="flex min-h-screen">
    <aside :class="['fixed inset-y-0 z-30 w-64 transform bg-brand-900 text-slate-200 transition lg:static lg:translate-x-0', open ? 'translate-x-0' : '-translate-x-full']">
      <div class="flex h-14 items-center gap-2 px-5 text-lg font-bold text-white">🚚 AgentOnWheels</div>
      <nav class="h-[calc(100vh-3.5rem)] overflow-y-auto px-3 pb-6 text-sm">
        <div class="mt-2 mb-1 px-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">Operations</div>
        <router-link to="/dashboard" class="nav" @click="open=false">📈 Dashboard</router-link>
        <router-link to="/control-tower" class="nav" @click="open=false">🛰️ Control tower</router-link>
        <template v-for="(items, g) in groups" :key="g">
          <div v-if="g !== 'Operations'" class="mt-4 mb-1 px-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">{{ g }}</div>
          <template v-if="g === 'Configuration'"><router-link to="/configuration" class="nav" @click="open=false">⚙️ Configuration hub</router-link></template>
          <template v-else><router-link v-for="i in items" :key="i.key" :to="'/r/' + i.key" class="nav" @click="open=false">{{ i.icon }} {{ i.title }}</router-link></template>
        </template>
        <div v-if="!groups" class="space-y-2 p-2"><div v-for="n in 10" :key="n" class="skeleton h-5 bg-white/10" /></div>
      </nav>
    </aside>
    <div class="flex min-w-0 flex-1 flex-col">
      <header class="sticky top-0 z-20 flex h-14 items-center gap-3 border-b bg-white px-4">
        <button class="btn-ghost lg:hidden" @click="open=!open">☰</button>
        <div class="flex-1" />
        <span class="hidden text-sm text-slate-500 sm:block">{{ clock }} · {{ tzLabel() }}</span>
        <span class="chip bg-slate-100 text-slate-700">{{ auth.user?.name }}</span>
        <button class="btn-ghost" @click="logout">Sign out</button>
      </header>
      <main class="min-w-0 flex-1 p-4 lg:p-6"><router-view :key="$route.fullPath.split('?')[0]" /></main>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api, { auth, logout } from './api'
import { tzLabel } from './format'
const groups = ref(null), open = ref(false), clock = ref('')
const route = useRoute()
let t
const tick = () => clock.value = new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: auth.user?.display_tz || 'Asia/Dubai' })
async function load() { if (auth.user && !groups.value) groups.value = (await api.get('meta/')).data.groups }
onMounted(() => { tick(); t = setInterval(tick, 15000); load() })
watch(() => auth.user, load)
onUnmounted(() => clearInterval(t))
</script>
<style>
.nav { @apply block rounded-lg px-2 py-1.5 text-slate-300 hover:bg-white/10 hover:text-white; }
.router-link-active.nav { @apply bg-white/15 text-white; }
</style>
