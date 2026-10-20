<template>
  <div class="grid min-h-dvh bg-app text-primary lg:h-dvh lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)] lg:overflow-hidden">
    <!-- ============ Brand panel (desktop) ============ -->
    <aside class="relative hidden flex-col justify-between overflow-hidden bg-slate-950 p-10 text-white lg:flex xl:p-14">
      <!-- Ambient background -->
      <div class="pointer-events-none absolute inset-0">
        <div class="login-glow absolute inset-0" />
        <div
          class="absolute inset-0 opacity-[0.07]"
          style="background-image: linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px); background-size: 44px 44px; mask-image: radial-gradient(ellipse 70% 60% at 50% 45%, #000 40%, transparent 100%);"
        />
      </div>

      <!-- Brand -->
      <div class="relative flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-500 shadow-lg shadow-primary-500/30 ring-1 ring-white/20">
          <Truck class="h-5 w-5" />
        </div>
        <div>
          <p class="text-[15px] font-semibold tracking-tight">AgentOnWheels</p>
          <p class="text-xs text-slate-400">Transport management system</p>
        </div>
      </div>

      <!-- Route illustration -->
      <div class="relative mx-auto my-6 w-full max-w-[520px] px-4 pt-12 pb-12">
        <svg viewBox="0 0 520 360" class="h-auto w-full overflow-visible" fill="none" aria-hidden="true">
          <defs>
            <linearGradient id="lg-route" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#818cf8" />
              <stop offset="100%" stop-color="#2dd4bf" />
            </linearGradient>
          </defs>

          <!-- Secondary lanes -->
          <path d="M90 70 C 200 95, 300 110, 420 120" stroke="#334155" stroke-width="1.5" stroke-dasharray="3 6" />
          <path d="M80 200 C 170 210, 220 250, 260 290" stroke="#334155" stroke-width="1.5" stroke-dasharray="3 6" />

          <!-- Primary corridor -->
          <path id="lg-corridor-a" d="M90 70 C 70 140, 70 170, 80 200 C 95 245, 140 300, 330 320" stroke="#312e81" stroke-width="7" stroke-linecap="round" />
          <path d="M90 70 C 70 140, 70 170, 80 200 C 95 245, 140 300, 330 320" stroke="url(#lg-route)" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="8 12" class="lg-flow" />

          <!-- East corridor -->
          <path id="lg-corridor-b" d="M420 120 C 360 180, 300 240, 260 290 C 280 305, 305 315, 330 320" stroke="#134e4a" stroke-width="5" stroke-linecap="round" />
          <path d="M420 120 C 360 180, 300 240, 260 290 C 280 305, 305 315, 330 320" stroke="#2dd4bf" stroke-width="2" stroke-linecap="round" stroke-dasharray="6 9" class="lg-flow-rev" />

          <!-- Moving vehicles -->
          <g class="lg-vehicle">
            <animateMotion dur="11s" repeatCount="indefinite" rotate="auto"><mpath href="#lg-corridor-a" /></animateMotion>
            <circle r="11" fill="#6366f1" fill-opacity="0.25" />
            <circle r="6.5" fill="#818cf8" stroke="#fff" stroke-width="1.5" />
          </g>
          <g class="lg-vehicle">
            <animateMotion dur="14s" repeatCount="indefinite" rotate="auto"><mpath href="#lg-corridor-b" /></animateMotion>
            <circle r="10" fill="#14b8a6" fill-opacity="0.25" />
            <circle r="6" fill="#2dd4bf" stroke="#fff" stroke-width="1.5" />
          </g>

          <!-- Hubs -->
          <g v-for="hub in hubs" :key="hub.label">
            <circle :cx="hub.x" :cy="hub.y" r="14" :stroke="hub.color" stroke-width="1.5" class="lg-pulse" :style="{ animationDelay: hub.delay }" />
            <circle :cx="hub.x" :cy="hub.y" r="5" :fill="hub.color" stroke="#fff" stroke-width="1.5" />
            <text :x="hub.x + hub.dx" :y="hub.y + hub.dy" :text-anchor="hub.anchor" fill="#e2e8f0" font-size="12" font-weight="600">
              {{ hub.label }}
            </text>
          </g>
        </svg>

        <!-- Floating status cards (illustrative) -->
        <div class="absolute right-0 top-0 flex items-center gap-2.5 rounded-xl border border-white/10 bg-slate-900/80 px-3 py-2 shadow-2xl backdrop-blur-md">
          <span class="relative flex h-2 w-2">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
            <span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
          </span>
          <span class="text-xs font-medium text-slate-200">Live trip tracking</span>
        </div>
        <div class="absolute bottom-0 left-0 flex items-center gap-2.5 rounded-xl border border-white/10 bg-slate-900/80 px-3 py-2 shadow-2xl backdrop-blur-md">
          <Route class="h-4 w-4 text-teal-300" />
          <span class="text-xs font-medium text-slate-200">Orders → trips → invoices</span>
        </div>
      </div>

      <!-- Value props -->
      <div class="relative space-y-6">
        <h2 class="max-w-md text-2xl font-semibold leading-tight tracking-tight xl:text-[28px]">
          Run every load from one control tower.
        </h2>
        <ul class="grid gap-4 sm:grid-cols-3">
          <li v-for="f in features" :key="f.title" class="space-y-1.5">
            <component :is="f.icon" class="h-5 w-5 text-primary-300" />
            <p class="text-sm font-medium text-white">{{ f.title }}</p>
            <p class="text-xs leading-relaxed text-slate-400">{{ f.text }}</p>
          </li>
        </ul>
      </div>
    </aside>

    <!-- ============ Sign-in panel ============ -->
    <main class="relative flex min-h-dvh flex-col px-5 py-6 sm:px-10 lg:min-h-0 lg:overflow-y-auto">
      <div class="flex items-center justify-between">
        <!-- Compact brand on mobile -->
        <div class="flex items-center gap-2.5 lg:invisible">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600 text-white shadow-sm">
            <Truck class="h-4 w-4" />
          </div>
          <span class="text-sm font-semibold tracking-tight">AgentOnWheels</span>
        </div>

        <button
          type="button"
          class="rounded-lg p-2 text-muted transition hover:bg-subtle hover:text-primary focus-ring"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          :title="isDark ? 'Light mode' : 'Dark mode'"
          @click="toggleTheme"
        >
          <Sun v-if="isDark" class="h-4 w-4" />
          <Moon v-else class="h-4 w-4" />
        </button>
      </div>

      <div class="flex flex-1 items-center justify-center py-10">
        <div :class="['w-full max-w-[380px]', isShaking && 'animate-shake']">
          <div class="mb-8 space-y-2">
            <h1 class="text-2xl font-semibold tracking-tight text-primary">Sign in</h1>
            <p class="text-sm text-muted">Welcome back. Enter your credentials to continue.</p>
          </div>

          <!-- Error -->
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="-translate-y-1 opacity-0"
            leave-active-class="transition duration-150"
            leave-to-class="opacity-0"
          >
            <div
              v-if="err"
              role="alert"
              class="mb-5 flex items-start gap-2.5 rounded-lg border border-danger-500/30 bg-danger-50 p-3 text-[13px] text-danger-700 dark:bg-danger-500/10 dark:text-rose-300"
            >
              <AlertCircle class="mt-px h-4 w-4 shrink-0" />
              <span class="leading-relaxed">{{ err }}</span>
            </div>
          </Transition>

          <form class="space-y-5" novalidate @submit.prevent="submit">
            <FormField label="Username" :error="uErr">
              <Input
                id="login-username"
                ref="usernameInputRef"
                v-model.trim="u"
                size="lg"
                autocomplete="username"
                autocapitalize="none"
                spellcheck="false"
                placeholder="your.username"
                :disabled="busy || isSuccess"
                @blur="u && validateUsername()"
                @input="uErr = ''"
              >
                <template #prefix><UserRound class="h-4 w-4" /></template>
              </Input>
            </FormField>

            <FormField :error="pErr">
              <template #label>
                <span>Password</span>
              </template>
              <Input
                id="login-password"
                ref="passwordInputRef"
                v-model="p"
                type="password"
                size="lg"
                autocomplete="current-password"
                placeholder="Enter your password"
                :disabled="busy || isSuccess"
                @input="pErr = ''"
              >
                <template #prefix><LockKeyhole class="h-4 w-4" /></template>
              </Input>
            </FormField>

            <div class="flex items-center justify-between">
              <Checkbox v-model="rememberMe" label="Remember me" :disabled="busy || isSuccess" />
              <button
                type="button"
                class="rounded text-[13px] font-medium text-primary-600 hover:underline focus-ring dark:text-primary-400"
                @click="showForgot = true"
              >
                Forgot password?
              </button>
            </div>

            <Button
              type="submit"
              size="lg"
              block
              :loading="busy && !isSuccess"
              :class="isSuccess && '!bg-success-600 hover:!bg-success-600'"
            >
              <template v-if="isSuccess">
                <CheckCircle2 class="h-4 w-4" />
                Signed in · redirecting…
              </template>
              <template v-else-if="busy">Signing in…</template>
              <template v-else>
                Sign in
                <ArrowRight class="h-4 w-4" />
              </template>
            </Button>
          </form>

          <!-- Demo access -->
          <div class="mt-8 flex items-center justify-between gap-3 rounded-lg border border-dashed border-border-strong px-3.5 py-3">
            <div class="min-w-0">
              <p class="text-xs font-medium text-primary">Demo environment</p>
              <p class="truncate text-[11px] text-muted">Use the seeded administrator account.</p>
            </div>
            <Button variant="secondary" size="sm" :disabled="busy || isSuccess" @click="quickFillDemo">
              <Sparkles class="h-3.5 w-3.5" />
              Fill demo
            </Button>
          </div>
        </div>
      </div>

      <p class="text-center text-[11px] text-muted">
        © {{ year }} AgentOnWheels · Need access? Contact your administrator.
      </p>
    </main>

    <!-- Forgot password -->
    <Modal
      :open="showForgot"
      title="Reset your password"
      description="Passwords are managed by your organisation's administrator."
      size="sm"
      @update:open="showForgot = $event"
    >
      <div class="space-y-3 text-sm text-secondary">
        <p>Self-service reset isn't enabled for this workspace. To regain access:</p>
        <ol class="list-decimal space-y-1.5 pl-5 text-[13px]">
          <li>Contact your fleet or IT administrator.</li>
          <li>Ask them to reset your password from the admin console.</li>
          <li>Sign in with the temporary password and change it.</li>
        </ol>
      </div>
      <template #footer>
        <Button variant="primary" @click="showForgot = false">Got it</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Truck, UserRound, LockKeyhole, ArrowRight, CheckCircle2, AlertCircle, Sun, Moon, Sparkles,
  Route, Radar, Workflow, ReceiptText,
} from 'lucide-vue-next'

import { login } from '../api'
import { useTheme } from '../composables/useTheme'
import Button from '../components/ui/Button.vue'
import Input from '../components/ui/Input.vue'
import FormField from '../components/ui/FormField.vue'
import Checkbox from '../components/ui/Checkbox.vue'
import Modal from '../components/ui/Modal.vue'

const router = useRouter()
const route = useRoute()
const { isDark, toggleTheme } = useTheme()

const REMEMBERED_USER_KEY = 'aow_remember_user'
const year = new Date().getFullYear()

const u = ref('')
const p = ref('')
const uErr = ref('')
const pErr = ref('')
const err = ref('')
const busy = ref(false)
const isSuccess = ref(false)
const isShaking = ref(false)
const rememberMe = ref(false)
const showForgot = ref(false)
const usernameInputRef = ref(null)
const passwordInputRef = ref(null)

const hubs = [
  { label: 'Delhi', x: 90, y: 70, color: '#818cf8', dx: 0, dy: -20, anchor: 'middle', delay: '0s' },
  { label: 'Ahmedabad', x: 80, y: 200, color: '#a5b4fc', dx: 16, dy: 4, anchor: 'start', delay: '0.6s' },
  { label: 'Kolkata', x: 420, y: 120, color: '#2dd4bf', dx: 0, dy: -20, anchor: 'middle', delay: '1.2s' },
  { label: 'Hyderabad', x: 260, y: 290, color: '#5eead4', dx: -14, dy: -12, anchor: 'end', delay: '1.8s' },
  { label: 'Bengaluru', x: 330, y: 320, color: '#34d399', dx: 0, dy: 28, anchor: 'middle', delay: '2.4s' },
]

const features = [
  { icon: Radar, title: 'Live visibility', text: 'Every trip, driver and vehicle on one board.' },
  { icon: Workflow, title: 'Faster dispatch', text: 'Turn orders into trips in a few clicks.' },
  { icon: ReceiptText, title: 'Clean billing', text: 'Rates, allowances and invoices in one place.' },
]

function validateUsername() {
  uErr.value = u.value ? '' : 'Enter your username.'
  return !uErr.value
}

function validatePassword() {
  pErr.value = p.value ? '' : 'Enter your password.'
  return !pErr.value
}

function quickFillDemo() {
  u.value = 'admin'
  p.value = 'admin'
  uErr.value = ''
  pErr.value = ''
  err.value = ''
  nextTick(() => passwordInputRef.value?.focus())
}

function shake() {
  isShaking.value = false
  requestAnimationFrame(() => {
    isShaking.value = true
    setTimeout(() => (isShaking.value = false), 400)
  })
}

async function submit() {
  const okUser = validateUsername()
  const okPass = validatePassword()
  if (!okUser || !okPass) {
    shake()
    ;(okUser ? passwordInputRef : usernameInputRef).value?.focus()
    return
  }

  busy.value = true
  err.value = ''

  try {
    await login(u.value, p.value)
    try {
      if (rememberMe.value) localStorage.setItem(REMEMBERED_USER_KEY, u.value)
      else localStorage.removeItem(REMEMBERED_USER_KEY)
    } catch {}
    isSuccess.value = true
    setTimeout(() => router.replace(route.query.next || '/dashboard'), 400)
  } catch (e) {
    shake()
    const status = e?.response?.status
    if (status === 401 || status === 400) {
      err.value = 'That username and password combination is incorrect.'
      p.value = ''
      nextTick(() => passwordInputRef.value?.focus())
    } else if (status === 429) {
      err.value = 'Too many attempts. Wait a minute, then try again.'
    } else {
      err.value = "We couldn't reach the server. Check your connection and try again."
    }
  } finally {
    busy.value = false
  }
}

onMounted(() => {
  let remembered = null
  try {
    remembered = localStorage.getItem(REMEMBERED_USER_KEY)
  } catch {}
  if (remembered) {
    u.value = remembered
    rememberMe.value = true
    nextTick(() => passwordInputRef.value?.focus())
  } else {
    nextTick(() => usernameInputRef.value?.focus())
  }
})
</script>

<style scoped>
.login-glow {
  background:
    radial-gradient(60% 50% at 15% 10%, rgb(99 102 241 / 0.35), transparent 70%),
    radial-gradient(50% 45% at 90% 85%, rgb(20 184 166 / 0.25), transparent 70%),
    radial-gradient(40% 40% at 70% 20%, rgb(139 92 246 / 0.18), transparent 70%);
}

.lg-flow { animation: lg-dash 1.8s linear infinite; }
.lg-flow-rev { animation: lg-dash 2.4s linear infinite reverse; }
@keyframes lg-dash {
  from { stroke-dashoffset: 40; }
  to { stroke-dashoffset: 0; }
}

.lg-pulse {
  transform-box: fill-box;
  transform-origin: center;
  animation: lg-pulse 3s ease-out infinite;
}
@keyframes lg-pulse {
  0% { transform: scale(0.35); opacity: 0.9; }
  100% { transform: scale(1.3); opacity: 0; }
}

.animate-shake { animation: shake 0.36s cubic-bezier(0.36, 0.07, 0.19, 0.97) both; }
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-6px); }
  40%, 80% { transform: translateX(6px); }
}

@media (prefers-reduced-motion: reduce) {
  .lg-flow, .lg-flow-rev, .lg-pulse, .animate-shake { animation: none !important; }
  .lg-vehicle { display: none; }
}
</style>
