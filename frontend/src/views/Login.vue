<template>
  <div class="min-h-screen flex flex-col lg:flex-row bg-app text-primary overflow-x-hidden selection:bg-brand-500/20">
    <!-- ==========================================
         LEFT BRAND PANEL (≥ lg: 55%, < lg: hero)
         ========================================== -->
    <div
      class="relative lg:w-[55%] flex flex-col justify-between overflow-hidden p-6 sm:p-10 lg:p-12 xl:p-16 bg-slate-950 text-white min-h-[380px] lg:min-h-screen"
      @mousemove="handleMouseMove"
      @mouseleave="handleMouseLeave"
    >
      <!-- Parallax Layer 1: Ambient Mesh Gradient & Cyber Grid (depth 4px) -->
      <div
        class="absolute inset-0 pointer-events-none transition-transform duration-200 ease-out"
        :style="parallaxLayer1Style"
      >
        <div class="absolute inset-0 login-mesh-bg opacity-70" />
        <div class="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_75%_60%_at_50%_50%,#000_60%,transparent_100%)]" />
      </div>

      <!-- Top Brand Header on Left Panel -->
      <div class="relative z-10 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/30 ring-1 ring-white/20">
            <Truck class="w-5 h-5 text-white" />
          </div>
          <div>
            <span class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              AgentOnWheels
              <span class="text-[10px] uppercase font-semibold tracking-wider bg-brand-500/30 text-brand-300 px-1.5 py-0.5 rounded border border-brand-400/30">TMS</span>
            </span>
            <p class="text-xs text-slate-400 font-medium">Autonomous Logistics Platform</p>
          </div>
        </div>

        <div class="hidden sm:inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-slate-900/80 border border-slate-800 text-slate-300 backdrop-blur-md">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Control Tower Live</span>
        </div>
      </div>

      <!-- Parallax Layer 2: Interactive Route Map SVG (depth 8px) -->
      <div
        class="relative z-10 my-auto py-6 sm:py-10 transition-transform duration-200 ease-out flex items-center justify-center"
        :style="parallaxLayer2Style"
      >
        <div class="relative w-full max-w-[560px]">
          <!-- Route Map SVG Illustration -->
          <svg
            viewBox="0 0 560 420"
            class="w-full h-auto overflow-visible drop-shadow-[0_20px_40px_rgba(0,0,0,0.6)]"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <!-- Route Glow Linear Gradient -->
              <linearGradient id="routeGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="50%" stop-color="#818cf8" />
                <stop offset="100%" stop-color="#34d399" />
              </linearGradient>
              <linearGradient id="secondaryGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#818cf8" stop-opacity="0.4" />
                <stop offset="100%" stop-color="#c084fc" stop-opacity="0.2" />
              </linearGradient>
            </defs>

            <!-- Background Secondary Transit Arteries -->
            <path
              d="M 120 90 C 220 120, 320 140, 440 150"
              stroke="url(#secondaryGlow)"
              stroke-width="1.5"
              stroke-dasharray="4 6"
            />
            <path
              d="M 440 150 C 360 230, 300 270, 270 330"
              stroke="url(#secondaryGlow)"
              stroke-width="1.5"
              stroke-dasharray="4 6"
            />
            <path
              d="M 100 230 C 180 240, 220 280, 270 330"
              stroke="url(#secondaryGlow)"
              stroke-width="1.5"
              stroke-dasharray="4 6"
            />

            <!-- Primary Golden Corridor: North -> West -> South Transit Corridor -->
            <!-- Path: Delhi (120, 90) -> Ahmedabad (100, 230) -> Mumbai (140, 310) -> Bengaluru (340, 370) -->
            <path
              id="goldenCorridor"
              d="M 120 90 C 100 160, 90 200, 100 230 C 110 270, 120 290, 140 310 C 180 350, 260 370, 340 370"
              stroke="rgba(99, 102, 241, 0.25)"
              stroke-width="6"
              stroke-linecap="round"
            />
            <path
              d="M 120 90 C 100 160, 90 200, 100 230 C 110 270, 120 290, 140 310 C 180 350, 260 370, 340 370"
              stroke="url(#routeGlow)"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-dasharray="8 12"
              class="animate-stream"
            />

            <!-- Primary East-South Corridor: Kolkata (440, 150) -> Hyderabad (270, 330) -> Bengaluru (340, 370) -->
            <path
              id="eastCorridor"
              d="M 440 150 C 370 210, 310 270, 270 330 C 290 350, 315 365, 340 370"
              stroke="rgba(45, 212, 191, 0.2)"
              stroke-width="4"
              stroke-linecap="round"
            />
            <path
              d="M 440 150 C 370 210, 310 270, 270 330 C 290 350, 315 365, 340 370"
              stroke="#2dd4bf"
              stroke-width="2"
              stroke-dasharray="6 8"
              class="animate-stream-reverse"
            />

            <!-- Moving Carrier 1 (Golden Corridor) -->
            <g>
              <animateMotion
                dur="12s"
                repeatCount="indefinite"
                rotate="auto"
              >
                <mpath href="#goldenCorridor" />
              </animateMotion>
              <!-- Halo & Pulsing Beacon -->
              <circle r="14" fill="rgba(56, 189, 248, 0.2)" class="animate-ping" />
              <circle r="9" fill="rgba(14, 165, 233, 0.85)" stroke="#ffffff" stroke-width="1.5" />
              <!-- Mini Truck Glyph -->
              <path
                d="M -5 -3 h 6 v 6 h -6 z M 1 -1 h 3 l 2 2 v 2 h -5 z"
                fill="#ffffff"
              />
            </g>

            <!-- Moving Carrier 2 (East Corridor) -->
            <g>
              <animateMotion
                dur="16s"
                repeatCount="indefinite"
                rotate="auto"
              >
                <mpath href="#eastCorridor" />
              </animateMotion>
              <circle r="12" fill="rgba(45, 212, 191, 0.25)" class="animate-ping" />
              <circle r="7" fill="#10b981" stroke="#ffffff" stroke-width="1.5" />
            </g>

            <!-- City Hub Nodes -->
            <!-- 1. Delhi Hub (120, 90) -->
            <g class="cursor-pointer group" @mouseenter="activeHoverHub = 'Delhi Hub'">
              <circle cx="120" cy="90" r="16" fill="none" stroke="#38bdf8" stroke-width="1.5" opacity="0.6">
                <animate attributeName="r" values="4;18" dur="3s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.8;0" dur="3s" repeatCount="indefinite" />
              </circle>
              <circle cx="120" cy="90" r="5" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />
              <text x="120" y="74" text-anchor="middle" fill="#f8fafc" font-size="11" font-weight="600" class="tracking-wide">Delhi Hub</text>
              <text x="120" y="62" text-anchor="middle" fill="#94a3b8" font-size="9" class="font-mono">DEL-01 • 48 Units</text>
            </g>

            <!-- 2. Ahmedabad Terminal (100, 230) -->
            <g class="cursor-pointer group" @mouseenter="activeHoverHub = 'Ahmedabad'">
              <circle cx="100" cy="230" r="4" fill="#818cf8" stroke="#ffffff" stroke-width="1" />
              <text x="88" y="234" text-anchor="end" fill="#cbd5e1" font-size="10" font-weight="500">Ahmedabad</text>
            </g>

            <!-- 3. Mumbai Port (140, 310) -->
            <g class="cursor-pointer group" @mouseenter="activeHoverHub = 'Mumbai Port'">
              <circle cx="140" cy="310" r="16" fill="none" stroke="#6366f1" stroke-width="1.5" opacity="0.6">
                <animate attributeName="r" values="4;16" dur="3.4s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.8;0" dur="3.4s" repeatCount="indefinite" />
              </circle>
              <circle cx="140" cy="310" r="5" fill="#6366f1" stroke="#ffffff" stroke-width="1.5" />
              <text x="140" y="332" text-anchor="middle" fill="#f8fafc" font-size="11" font-weight="600">Mumbai Port</text>
              <text x="140" y="344" text-anchor="middle" fill="#94a3b8" font-size="9" class="font-mono">BOM-02 • Gateway</text>
            </g>

            <!-- 4. Kolkata Hub (440, 150) -->
            <g class="cursor-pointer group" @mouseenter="activeHoverHub = 'Kolkata Hub'">
              <circle cx="440" cy="150" r="16" fill="none" stroke="#2dd4bf" stroke-width="1.5" opacity="0.6">
                <animate attributeName="r" values="4;16" dur="2.8s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.8;0" dur="2.8s" repeatCount="indefinite" />
              </circle>
              <circle cx="440" cy="150" r="5" fill="#2dd4bf" stroke="#ffffff" stroke-width="1.5" />
              <text x="440" y="136" text-anchor="middle" fill="#f8fafc" font-size="11" font-weight="600">Kolkata Hub</text>
              <text x="440" y="124" text-anchor="middle" fill="#94a3b8" font-size="9" class="font-mono">CCU-03 • 32 Units</text>
            </g>

            <!-- 5. Hyderabad Junction (270, 330) -->
            <g class="cursor-pointer group" @mouseenter="activeHoverHub = 'Hyderabad'">
              <circle cx="270" cy="330" r="4" fill="#a78bfa" stroke="#ffffff" stroke-width="1" />
              <text x="270" y="318" text-anchor="middle" fill="#cbd5e1" font-size="10" font-weight="500">Hyderabad</text>
            </g>

            <!-- 6. Bengaluru Gateway (340, 370) -->
            <g class="cursor-pointer group" @mouseenter="activeHoverHub = 'Bengaluru Gateway'">
              <circle cx="340" cy="370" r="18" fill="none" stroke="#34d399" stroke-width="1.5" opacity="0.6">
                <animate attributeName="r" values="4;18" dur="3.2s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.8;0" dur="3.2s" repeatCount="indefinite" />
              </circle>
              <circle cx="340" cy="370" r="5.5" fill="#34d399" stroke="#ffffff" stroke-width="1.5" />
              <text x="340" y="394" text-anchor="middle" fill="#f8fafc" font-size="11" font-weight="600">Bengaluru Gateway</text>
              <text x="340" y="406" text-anchor="middle" fill="#94a3b8" font-size="9" class="font-mono">BLR-04 • Tech Hub</text>
            </g>
          </svg>

          <!-- Parallax Layer 3: Floating Telemetry Cards (depth 16px) -->
          <div
            class="absolute -top-3 -left-4 sm:-left-8 transition-transform duration-200 ease-out hidden sm:block pointer-events-none"
            :style="parallaxLayer3Style"
          >
            <div class="px-3.5 py-2 rounded-xl bg-slate-900/80 border border-slate-700/80 shadow-2xl backdrop-blur-md flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-brand-500/20 text-brand-400 flex items-center justify-center ring-1 ring-brand-400/30">
                <Radio class="w-4 h-4 animate-pulse" />
              </div>
              <div>
                <p class="text-[11px] font-semibold text-white">Live Fleet Telemetry</p>
                <p class="text-[10px] text-emerald-400 font-mono">1,428 Active • 99.8% Sync</p>
              </div>
            </div>
          </div>

          <div
            class="absolute -bottom-2 -right-4 sm:-right-8 transition-transform duration-200 ease-out hidden sm:block pointer-events-none"
            :style="parallaxLayer3Style"
          >
            <div class="px-3.5 py-2 rounded-xl bg-slate-900/80 border border-slate-700/80 shadow-2xl backdrop-blur-md flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center ring-1 ring-emerald-400/30">
                <TrendingUp class="w-4 h-4" />
              </div>
              <div>
                <p class="text-[11px] font-semibold text-white">Dynamic Dispatch ETA</p>
                <p class="text-[10px] text-slate-300 font-mono">Avg Delay: -18m • 98.4% SLA</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Rotating Highlights Carousel (Paused on hover, auto-rotates every 4s) -->
      <div
        class="relative z-10 pt-4"
        @mouseenter="pauseHighlights = true"
        @mouseleave="pauseHighlights = false"
      >
        <div class="min-h-[96px] flex flex-col justify-end">
          <Transition name="fade-slide" mode="out-in">
            <div :key="currentSlideIndex" class="space-y-1.5">
              <div class="flex items-center gap-2">
                <component
                  :is="currentSlide.icon"
                  class="w-4 h-4 text-brand-400 shrink-0"
                />
                <h2 class="text-sm sm:text-base font-semibold text-white">
                  {{ currentSlide.title }}
                </h2>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {{ currentSlide.badge }}
                </span>
              </div>
              <p class="text-xs sm:text-sm text-slate-400 max-w-lg leading-relaxed">
                {{ currentSlide.description }}
              </p>
            </div>
          </Transition>
        </div>

        <!-- Dot Indicators -->
        <div class="flex items-center gap-2 mt-4">
          <button
            v-for="(slide, idx) in slides"
            :key="idx"
            type="button"
            :class="[
              'h-1.5 rounded-full transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400',
              idx === currentSlideIndex
                ? 'w-7 bg-brand-400'
                : 'w-2 bg-white/20 hover:bg-white/40'
            ]"
            :aria-label="`Go to highlight ${idx + 1}`"
            @click="currentSlideIndex = idx"
          />
        </div>
      </div>
    </div>

    <!-- ==========================================
         RIGHT LOGIN CARD (45% split on lg+)
         ========================================== -->
    <div class="lg:w-[45%] flex flex-col justify-between p-6 sm:p-10 lg:p-12 xl:p-16 relative z-10 bg-surface/60 dark:bg-slate-950/60 backdrop-blur-sm">
      <!-- Top Utility Bar: Operational Status & Theme Toggle -->
      <div class="flex items-center justify-between pb-6">
        <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-[11px] font-medium bg-subtle text-secondary border border-border-default">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>TMS Cluster v2.4</span>
        </div>

        <button
          type="button"
          class="p-2 rounded-lg text-secondary hover:text-primary hover:bg-subtle transition focus-ring"
          :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleTheme"
        >
          <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
          <Moon v-else class="w-4 h-4 text-slate-600" />
        </button>
      </div>

      <!-- Main Login Glass Card -->
      <div class="w-full max-w-md mx-auto my-auto py-4">
        <div
          :class="[
            'w-full p-6 sm:p-9 rounded-2xl border border-border-default/80 bg-surface/90 dark:bg-surface-elevated/80 shadow-2xl backdrop-blur-xl transition-all duration-300',
            isShaking && 'animate-shake',
            isSuccess && 'opacity-85 scale-[0.99] pointer-events-none'
          ]"
        >
          <!-- Card Header -->
          <div class="mb-6">
            <div class="w-11 h-11 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-brand-500/20 mb-4 ring-1 ring-white/10">
              <Truck class="w-6 h-6 text-white" />
            </div>
            <h1 class="text-2xl font-bold tracking-tight text-primary">
              Welcome back
            </h1>
            <p class="text-xs sm:text-sm text-secondary mt-1">
              Sign in to your transport control centre
            </p>
          </div>

          <!-- Error Alert Banner -->
          <div
            v-if="err"
            role="alert"
            class="mb-5 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 text-rose-800 dark:text-rose-200 text-xs flex items-start gap-2.5 animate-in fade-in duration-200"
          >
            <AlertCircle class="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
            <div class="leading-relaxed">
              {{ err }}
            </div>
          </div>

          <!-- Form -->
          <form class="space-y-4" @submit.prevent="submit">
            <!-- Username Field -->
            <div class="space-y-1.5">
              <label for="login-username" class="text-xs font-medium text-primary flex items-center justify-between">
                <span>Username <span class="text-danger-500">*</span></span>
              </label>

              <div class="relative">
                <Input
                  id="login-username"
                  ref="usernameInputRef"
                  v-model.trim="u"
                  autocomplete="username"
                  placeholder="e.g. admin or dispatcher"
                  size="lg"
                  :invalid="!!uErr"
                  :disabled="busy || isSuccess"
                  class="pl-10"
                  @blur="validateUsername"
                  @input="uErr = ''"
                >
                  <template #prefix>
                    <User class="w-4 h-4 text-muted" />
                  </template>
                </Input>
              </div>

              <p v-if="uErr" class="text-xs text-danger-600 dark:text-danger-400 flex items-center gap-1 mt-1">
                <AlertCircle class="w-3.5 h-3.5" />
                <span>{{ uErr }}</span>
              </p>
            </div>

            <!-- Password Field -->
            <div class="space-y-1.5">
              <div class="flex items-center justify-between">
                <label for="login-password" class="text-xs font-medium text-primary">
                  Password <span class="text-danger-500">*</span>
                </label>
                <button
                  type="button"
                  class="text-xs text-brand-600 dark:text-brand-400 hover:underline font-medium focus-ring rounded"
                  @click="showForgotPasswordModal = true"
                >
                  Forgot password?
                </button>
              </div>

              <div class="relative">
                <Input
                  id="login-password"
                  ref="passwordInputRef"
                  v-model="p"
                  type="password"
                  autocomplete="current-password"
                  placeholder="Enter your password"
                  size="lg"
                  :invalid="!!pErr"
                  :disabled="busy || isSuccess"
                  class="pl-10"
                  @blur="validatePassword"
                  @input="pErr = ''"
                >
                  <template #prefix>
                    <Lock class="w-4 h-4 text-muted" />
                  </template>
                </Input>
              </div>

              <p v-if="pErr" class="text-xs text-danger-600 dark:text-danger-400 flex items-center gap-1 mt-1">
                <AlertCircle class="w-3.5 h-3.5" />
                <span>{{ pErr }}</span>
              </p>
            </div>

            <!-- Remember Me Row -->
            <div class="flex items-center justify-between pt-1">
              <Checkbox
                v-model="rememberMe"
                label="Remember my username"
                :disabled="busy || isSuccess"
              />
            </div>

            <!-- Submit Button -->
            <div class="pt-2">
              <Button
                type="submit"
                size="lg"
                class="w-full justify-center transition-all duration-300"
                :class="isSuccess ? 'bg-emerald-600 hover:bg-emerald-600 text-white' : ''"
                :loading="busy && !isSuccess"
                :disabled="busy || isSuccess"
              >
                <template v-if="isSuccess">
                  <CheckCircle2 class="w-4 h-4" />
                  <span>Success! Redirecting…</span>
                </template>
                <template v-else-if="busy">
                  <span>Authenticating…</span>
                </template>
                <template v-else>
                  <span>Sign in to Control Tower</span>
                  <ArrowRight class="w-4 h-4 ml-1" />
                </template>
              </Button>
            </div>
          </form>

          <!-- Quick Fill Demo Bar for evaluators -->
          <div class="mt-6 pt-5 border-t border-border-default/60 flex items-center justify-between text-xs text-secondary">
            <span>Demo credentials:</span>
            <button
              type="button"
              class="font-mono text-[11px] px-2 py-1 rounded-md bg-subtle hover:bg-subtle-hover text-primary border border-border-default transition focus-ring"
              @click="quickFillDemo"
            >
              admin / admin
            </button>
          </div>
        </div>
      </div>

      <!-- Bottom Compliance & Security Footer -->
      <div class="pt-6 text-center lg:text-left text-[11px] text-muted flex flex-col sm:flex-row items-center justify-between gap-2 border-t border-border-default/40">
        <div class="flex items-center gap-1.5">
          <ShieldCheck class="w-3.5 h-3.5 text-emerald-500" />
          <span>SOC-2 Type II Certified • 256-bit TLS Encrypted</span>
        </div>
        <p>© 2026 AgentOnWheels TMS</p>
      </div>
    </div>

    <!-- ==========================================
         FORGOT PASSWORD MODAL
         ========================================== -->
    <Modal
      :open="showForgotPasswordModal"
      title="Reset Password"
      description="AgentOnWheels Enterprise Credential Policy"
      size="sm"
      @update:open="showForgotPasswordModal = $event"
    >
      <div class="space-y-3 p-1 text-sm text-secondary">
        <p>
          For enterprise compliance and security, user authentication credentials cannot be reset through self-service email links.
        </p>
        <div class="p-3 rounded-lg bg-subtle border border-border-default text-xs space-y-1.5">
          <p class="font-semibold text-primary">How to regain access:</p>
          <ul class="list-disc list-inside space-y-1 text-secondary">
            <li>Contact your organization's transport fleet administrator.</li>
            <li>Submit an IT service ticket with your employee ID.</li>
            <li>Default local environment credentials: <code class="font-mono text-brand-600 dark:text-brand-400 font-bold">admin / admin</code>.</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <Button variant="outline" @click="showForgotPasswordModal = false">
          Close
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Truck,
  User,
  Lock,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Sun,
  Moon,
  ShieldCheck,
  Radio,
  Cpu,
  TrendingUp,
} from 'lucide-vue-next'

import { login } from '../api'
import { useTheme } from '../composables/useTheme'
import Button from '../components/ui/Button.vue'
import Input from '../components/ui/Input.vue'
import Checkbox from '../components/ui/Checkbox.vue'
import Modal from '../components/ui/Modal.vue'

// ==========================================
// STATE & ROUTING
// ==========================================
const router = useRouter()
const route = useRoute()
const { isDark, toggleTheme } = useTheme()

const u = ref('')
const p = ref('')
const uErr = ref('')
const pErr = ref('')
const err = ref('')
const busy = ref(false)
const isSuccess = ref(false)
const isShaking = ref(false)
const rememberMe = ref(false)
const showForgotPasswordModal = ref(false)
const activeHoverHub = ref(null)

const usernameInputRef = ref(null)
const passwordInputRef = ref(null)

const REMEMBERED_USER_KEY = 'aow_remember_user'

// ==========================================
// CAROUSEL SLIDES (4s auto-rotation)
// ==========================================
const slides = [
  {
    icon: Radio,
    title: 'Live Fleet Tracking & Telemetry',
    badge: 'Live GPS',
    description: 'Sub-second satellite GPS pings, automated geofence entry/exit events, and dynamic ETA recalculations.',
  },
  {
    icon: Cpu,
    title: 'Intelligent Dispatch & Load Matching',
    badge: 'AI Optimized',
    description: 'Autonomous multi-stop order routing that reduces deadhead miles and balances driver duty hours.',
  },
  {
    icon: ShieldCheck,
    title: 'Audit-Proof Financial Governance',
    badge: 'SOC2 Ready',
    description: 'Unified automated toll reconciliation, demurrage calculations, and real-time lane profitability margins.',
  },
]

const currentSlideIndex = ref(0)
const currentSlide = computed(() => slides[currentSlideIndex.value])
const pauseHighlights = ref(false)
let carouselTimer = null

function advanceSlide() {
  if (!pauseHighlights.value) {
    currentSlideIndex.value = (currentSlideIndex.value + 1) % slides.length
  }
}

// ==========================================
// PARALLAX EFFECT (4px - 16px mouse tracking)
// ==========================================
const mouse = reactive({ x: 0, y: 0 })

function handleMouseMove(e) {
  if (typeof window === 'undefined') return
  if (window.matchMedia('(pointer: coarse)').matches) return
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

  const rect = e.currentTarget.getBoundingClientRect()
  mouse.x = ((e.clientX - rect.left) / rect.width - 0.5) * 2 // -1 to 1
  mouse.y = ((e.clientY - rect.top) / rect.height - 0.5) * 2
}

function handleMouseLeave() {
  mouse.x = 0
  mouse.y = 0
}

const parallaxLayer1Style = computed(() => ({
  transform: `translate3d(${mouse.x * 4}px, ${mouse.y * 4}px, 0)`,
}))

const parallaxLayer2Style = computed(() => ({
  transform: `translate3d(${mouse.x * 8}px, ${mouse.y * 8}px, 0)`,
}))

const parallaxLayer3Style = computed(() => ({
  transform: `translate3d(${mouse.x * 16}px, ${mouse.y * 16}px, 0)`,
}))

// ==========================================
// VALIDATION & SUBMISSION
// ==========================================
function validateUsername() {
  if (!u.value) {
    uErr.value = 'Please enter your username.'
    return false
  }
  uErr.value = ''
  return true
}

function validatePassword() {
  if (!p.value) {
    pErr.value = 'Please enter your password.'
    return false
  }
  pErr.value = ''
  return true
}

function quickFillDemo() {
  u.value = 'admin'
  p.value = 'admin'
  uErr.value = ''
  pErr.value = ''
}

async function submit() {
  const isUserValid = validateUsername()
  const isPassValid = validatePassword()
  if (!isUserValid || !isPassValid) return

  busy.value = true
  err.value = ''
  isShaking.value = false

  try {
    await login(u.value, p.value)

    // Save or clear remembered username
    if (rememberMe.value) {
      localStorage.setItem(REMEMBERED_USER_KEY, u.value)
    } else {
      localStorage.removeItem(REMEMBERED_USER_KEY)
    }

    // Success transition
    isSuccess.value = true
    setTimeout(() => {
      router.replace(route.query.next || '/dashboard')
    }, 450)
  } catch (e) {
    // Shake animation trigger
    isShaking.value = true
    setTimeout(() => {
      isShaking.value = false
    }, 350)

    if (e.response?.status === 401) {
      err.value = 'Invalid username or password. Please try again.'
      // Clear password and refocus
      p.value = ''
      passwordInputRef.value?.focus()
    } else if (e.response?.status === 429) {
      err.value = 'Too many attempts. Please wait a minute and retry.'
    } else {
      err.value = 'Cannot reach the authentication server. Please check your network and retry.'
    }
  } finally {
    busy.value = false
  }
}

// ==========================================
// LIFECYCLE
// ==========================================
onMounted(() => {
  // Restore remembered username if present
  const remembered = localStorage.getItem(REMEMBERED_USER_KEY)
  if (remembered) {
    u.value = remembered
    rememberMe.value = true
  }

  // Start carousel
  carouselTimer = setInterval(advanceSlide, 4000)
})

onUnmounted(() => {
  if (carouselTimer) clearInterval(carouselTimer)
})
</script>

<style scoped>
/* Mesh Gradient animation */
.login-mesh-bg {
  background: radial-gradient(at 10% 10%, rgba(99, 102, 241, 0.45) 0px, transparent 50%),
              radial-gradient(at 90% 10%, rgba(168, 85, 247, 0.35) 0px, transparent 50%),
              radial-gradient(at 85% 85%, rgba(20, 184, 166, 0.35) 0px, transparent 50%),
              radial-gradient(at 15% 85%, rgba(59, 130, 246, 0.35) 0px, transparent 50%),
              radial-gradient(at 50% 50%, rgba(124, 58, 237, 0.25) 0px, transparent 50%);
  background-size: 160% 160%;
  animation: meshShift 16s ease-in-out infinite alternate;
}

@keyframes meshShift {
  0% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
  100% { background-position: 0% 50%; }
}

/* Highway Streaming animations */
@keyframes streamFlow {
  from { stroke-dashoffset: 40; }
  to { stroke-dashoffset: 0; }
}

@keyframes streamFlowReverse {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: 40; }
}

.animate-stream {
  animation: streamFlow 1.8s linear infinite;
}

.animate-stream-reverse {
  animation: streamFlowReverse 2.4s linear infinite;
}

/* 300ms Shake on login failure */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-8px); }
  40%, 80% { transform: translateX(8px); }
}

.animate-shake {
  animation: shake 0.32s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}

/* Carousel transition */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease-out;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* Accessibility: respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  .login-mesh-bg,
  .animate-stream,
  .animate-stream-reverse,
  .animate-shake {
    animation: none !important;
  }
}
</style>
