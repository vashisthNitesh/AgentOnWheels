<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-900 to-brand-600 p-4">
    <form class="card w-full max-w-sm p-8" @submit.prevent="submit">
      <h1 class="text-2xl font-bold text-slate-900">🚚 AgentOnWheels</h1>
      <p class="mb-6 text-sm text-slate-500">Sign in to your transport control centre</p>
      <label class="mb-1 block text-sm font-medium">Username</label>
      <input v-model.trim="u" class="input mb-4" autocomplete="username" autofocus required />
      <label class="mb-1 block text-sm font-medium">Password</label>
      <div class="relative mb-4">
        <input v-model="p" :type="show ? 'text' : 'password'" class="input pr-16" autocomplete="current-password" required />
        <button type="button" class="absolute right-2 top-2 text-xs text-brand-600" @click="show=!show">{{ show ? 'Hide' : 'Show' }}</button>
      </div>
      <p v-if="err" class="mb-3 rounded bg-rose-50 p-2 text-sm text-rose-700">{{ err }}</p>
      <button class="btn-primary w-full justify-center" :disabled="busy">{{ busy ? 'Signing in…' : 'Sign in' }}</button>
    </form>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { login } from '../api'
const u = ref(''), p = ref(''), err = ref(''), busy = ref(false), show = ref(false)
const router = useRouter(), route = useRoute()
async function submit() {
  busy.value = true; err.value = ''
  try { await login(u.value, p.value); router.replace(route.query.next || '/dashboard') }
  catch (e) { err.value = e.response?.status === 401 ? 'Wrong username or password.' : e.response?.status === 429 ? 'Too many attempts. Wait a minute and retry.' : 'Cannot reach the server. Please retry.' }
  finally { busy.value = false }
}
</script>
