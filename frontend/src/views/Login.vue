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
      <div class="relative">
        <BrandLogo size="lg" with-badge invert />
      </div>

      <!-- Interactive Brand Showcase -->
      <div class="relative my-auto w-full max-w-lg space-y-6 py-6">
        <!-- Headline -->
        <div class="space-y-2">
          <h1 class="text-2xl font-bold tracking-tight text-white xl:text-3xl xl:leading-tight">
            Connected freight & fleet intelligence.
          </h1>
          <p class="text-sm leading-relaxed text-slate-300">
            Dispatch loads in seconds, monitor live vehicle telemetry, and reconcile automated freight billing.
          </p>
        </div>

        <!-- Interactive Mode Switcher Tabs -->
        <div class="flex items-center gap-1.5 rounded-xl border border-white/10 bg-slate-900/80 p-1 backdrop-blur-md">
          <button
            type="button"
            :class="[
              'flex-1 rounded-lg px-3 py-2 text-xs font-semibold transition-all duration-150',
              demoTab === 'dispatch'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            ]"
            @click="demoTab = 'dispatch'"
          >
            Dispatch flow
          </button>
          <button
            type="button"
            :class="[
              'flex-1 rounded-lg px-3 py-2 text-xs font-semibold transition-all duration-150',
              demoTab === 'telematics'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            ]"
            @click="demoTab = 'telematics'"
          >
            Fleet telematics
          </button>
          <button
            type="button"
            :class="[
              'flex-1 rounded-lg px-3 py-2 text-xs font-semibold transition-all duration-150',
              demoTab === 'billing'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            ]"
            @click="demoTab = 'billing'"
          >
            Fast billing
          </button>
        </div>

        <!-- Tab 1: Dispatch Flow Card -->
        <div
          v-if="demoTab === 'dispatch'"
          class="rounded-2xl border border-white/10 bg-slate-900/70 p-5 backdrop-blur-xl shadow-2xl space-y-4"
        >
          <div class="flex items-center justify-between border-b border-white/10 pb-3">
            <div>
              <span class="font-mono text-xs font-medium text-primary-400">ORDER #AXL-8840</span>
              <p class="text-xs text-slate-300 font-medium mt-0.5">Commercial Freight · 28 Ton</p>
            </div>
            <span
              :class="[
                'rounded-full px-2.5 py-1 text-[11px] font-semibold border',
                dispatchStage === 0 && 'bg-blue-500/10 text-blue-300 border-blue-500/20',
                dispatchStage === 1 && 'bg-amber-500/10 text-amber-300 border-amber-500/20',
                dispatchStage === 2 && 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20',
                dispatchStage === 3 && 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
              ]"
            >
              {{ dispatchStageLabels[dispatchStage] }}
            </span>
          </div>

          <!-- Route corridor -->
          <div class="space-y-1 text-xs">
            <div class="flex items-center justify-between text-slate-300 font-medium">
              <span>Port Logistics Terminal</span>
              <span class="text-slate-500">➔</span>
              <span>Inland Distribution Hub</span>
            </div>
            <p class="text-[11px] text-slate-400">Assigned Asset: Volvo FH16 · Driver: Marcus Vance</p>
          </div>

          <!-- Stepper Visualization -->
          <div class="grid grid-cols-4 gap-2 pt-1">
            <div
              v-for="(st, idx) in ['Created', 'Assigned', 'In transit', 'Delivered']"
              :key="st"
              class="space-y-1.5"
            >
              <div
                :class="[
                  'h-1.5 rounded-full transition-all duration-300',
                  idx <= dispatchStage ? 'bg-primary-500 shadow-sm shadow-primary-500/50' : 'bg-slate-800'
                ]"
              />
              <p
                :class="[
                  'text-[10px] font-medium text-center truncate',
                  idx <= dispatchStage ? 'text-slate-200' : 'text-slate-500'
                ]"
              >
                {{ st }}
              </p>
            </div>
          </div>

          <!-- Interactive Advance Button -->
          <button
            type="button"
            class="w-full flex items-center justify-center gap-2 rounded-xl bg-white/10 hover:bg-white/15 active:bg-white/20 py-2.5 px-4 text-xs font-semibold text-white transition border border-white/10"
            @click="dispatchStage = (dispatchStage + 1) % 4"
          >
            <span>{{ dispatchStage === 3 ? '↺ Reset dispatch demo' : `Simulate next step (${dispatchStageLabels[(dispatchStage + 1) % 4]}) →` }}</span>
          </button>
        </div>

        <!-- Tab 2: Fleet Telematics Card -->
        <div
          v-else-if="demoTab === 'telematics'"
          class="rounded-2xl border border-white/10 bg-slate-900/70 p-5 backdrop-blur-xl shadow-2xl space-y-4"
        >
          <div class="flex items-center justify-between border-b border-white/10 pb-3">
            <div>
              <p class="text-xs font-semibold text-white">Truck #104 · Heavy Hauler</p>
              <p class="text-[11px] text-slate-400">Mercedes Actros 2645 · Highway Corridor</p>
            </div>
            <span class="flex items-center gap-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 text-[11px] font-medium text-emerald-300">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Engine Online
            </span>
          </div>

          <!-- Telemetry Grid -->
          <div class="grid grid-cols-3 gap-2.5">
            <div class="rounded-xl border border-white/5 bg-slate-950/50 p-2.5 text-center">
              <p class="text-[10px] uppercase font-semibold text-slate-400">Speed</p>
              <p class="text-lg font-bold text-white mt-0.5">{{ truckSpeed }} <span class="text-xs font-normal text-slate-400">km/h</span></p>
            </div>
            <div class="rounded-xl border border-white/5 bg-slate-950/50 p-2.5 text-center">
              <p class="text-[10px] uppercase font-semibold text-slate-400">Fuel level</p>
              <p class="text-lg font-bold text-teal-300 mt-0.5">84%</p>
            </div>
            <div class="rounded-xl border border-white/5 bg-slate-950/50 p-2.5 text-center">
              <p class="text-[10px] uppercase font-semibold text-slate-400">Reefer temp</p>
              <p class="text-lg font-bold text-sky-300 mt-0.5">+3.8°C</p>
            </div>
          </div>

          <!-- Speed Simulation Controls -->
          <div class="flex items-center justify-between gap-2 pt-1 text-xs">
            <span class="text-[11px] text-slate-400">Simulate cruise:</span>
            <div class="flex items-center gap-1.5">
              <button
                v-for="s in [65, 82, 95]"
                :key="s"
                type="button"
                :class="[
                  'rounded-lg px-2.5 py-1 text-xs font-medium transition border',
                  truckSpeed === s
                    ? 'bg-primary-600 text-white border-primary-500'
                    : 'bg-white/5 text-slate-300 border-white/10 hover:bg-white/10'
                ]"
                @click="truckSpeed = s"
              >
                {{ s }} km/h
              </button>
            </div>
          </div>
        </div>

        <!-- Tab 3: Fast Billing Card -->
        <div
          v-else
          class="rounded-2xl border border-white/10 bg-slate-900/70 p-5 backdrop-blur-xl shadow-2xl space-y-4"
        >
          <div class="flex items-center justify-between border-b border-white/10 pb-3">
            <div>
              <p class="text-xs font-semibold text-white">Rate Master & Invoicing</p>
              <p class="text-[11px] text-slate-400">Dynamic tariff calculation</p>
            </div>
            <span class="font-mono text-xs font-bold text-primary-300">$2,450.00</span>
          </div>

          <!-- Pricing breakdown -->
          <div class="space-y-1.5 text-xs text-slate-300">
            <div class="flex justify-between">
              <span class="text-slate-400">Base freight (420 km)</span>
              <span>$1,950.00</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Fuel surcharge indexed</span>
              <span>+$280.00</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Loading & detention fee</span>
              <span>+$220.00</span>
            </div>
          </div>

          <!-- Action -->
          <button
            type="button"
            :class="[
              'w-full flex items-center justify-center gap-2 rounded-xl py-2.5 px-4 text-xs font-semibold transition border shadow-sm',
              invoiceCreated
                ? 'bg-emerald-600/90 text-white border-emerald-500'
                : 'bg-primary-600 hover:bg-primary-500 text-white border-primary-500'
            ]"
            @click="invoiceCreated = !invoiceCreated"
          >
            <span>{{ invoiceCreated ? '✓ Tax invoice #INV-4029 generated' : 'Generate automated invoice →' }}</span>
          </button>
        </div>

        <!-- Universal feature points -->
        <div class="flex flex-wrap items-center gap-y-2 gap-x-4 text-[11px] text-slate-400 pt-1">
          <span class="flex items-center gap-1.5">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Live GPS telemetry
          </span>
          <span>•</span>
          <span>Multi-currency rates</span>
          <span>•</span>
          <span>Instant driver POD</span>
          <span>•</span>
          <span>Audit-ready trails</span>
        </div>
      </div>
    </aside>

    <!-- ============ Sign-in panel ============ -->
    <main class="relative flex min-h-dvh flex-col px-5 py-6 sm:px-10 lg:min-h-0 lg:overflow-y-auto">
      <div class="flex items-center justify-between">
        <!-- Compact brand on mobile -->
        <div class="flex items-center gap-2.5 lg:invisible">
          <BrandLogo size="sm" with-badge />
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
        © {{ year }} Axle · Need access? Contact your administrator.
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
  UserRound, LockKeyhole, ArrowRight, CheckCircle2, AlertCircle, Sun, Moon, Sparkles,
} from 'lucide-vue-next'

import { login } from '../api'
import { useTheme } from '../composables/useTheme'
import Button from '../components/ui/Button.vue'
import Input from '../components/ui/Input.vue'
import FormField from '../components/ui/FormField.vue'
import Checkbox from '../components/ui/Checkbox.vue'
import Modal from '../components/ui/Modal.vue'
import BrandLogo from '../components/brand/BrandLogo.vue'

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

const demoTab = ref('dispatch')
const dispatchStage = ref(2)
const dispatchStageLabels = ['Order Created', 'Driver Assigned', 'In Transit · 84 km/h', 'Delivered & Signed']
const truckSpeed = ref(82)
const invoiceCreated = ref(false)

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

.animate-shake { animation: shake 0.36s cubic-bezier(0.36, 0.07, 0.19, 0.97) both; }
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-6px); }
  40%, 80% { transform: translateX(6px); }
}

@media (prefers-reduced-motion: reduce) {
  .animate-shake { animation: none !important; }
}
</style>
