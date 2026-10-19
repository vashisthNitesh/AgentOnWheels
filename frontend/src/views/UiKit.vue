<template>
  <div class="min-h-screen bg-app text-primary p-6 lg:p-10 transition-colors duration-200">
    <div class="max-w-7xl mx-auto space-y-12">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-default pb-6">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs uppercase tracking-wider font-semibold text-primary-600 dark:text-primary-400">Design System</span>
            <span class="chip bg-accent-50 text-accent-700 dark:bg-accent-950/50 dark:text-accent-300">Phase 1 Foundations</span>
          </div>
          <h1 class="text-3xl font-bold tracking-tight mt-1">AgentOnWheels UI Kit & Visual Test Bench</h1>
          <p class="text-secondary text-sm mt-1">Tokens, typography, status vocabulary, and theme primitives.</p>
        </div>

        <!-- Theme Mode Switcher -->
        <div class="flex items-center gap-1 bg-surface border border-border-default rounded-lg p-1 shadow-xs">
          <button
            v-for="mode in ['light', 'dark', 'system']"
            :key="mode"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5',
              theme === mode
                ? 'bg-primary-600 text-white shadow-xs dark:bg-primary-500'
                : 'text-secondary hover:text-primary hover:bg-subtle'
            ]"
            @click="setTheme(mode)"
          >
            <component :is="modeIcon(mode)" class="w-3.5 h-3.5" />
            <span class="capitalize">{{ mode }}</span>
          </button>
        </div>
      </div>

      <!-- Color Palette Showcase -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold flex items-center gap-2">
          <span>🎨 Color Tokens (RGB Triplet Scaled)</span>
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Primary Indigo -->
          <div class="card p-4 space-y-3">
            <div class="text-sm font-semibold">Primary (Indigo #4F46E5)</div>
            <div class="grid grid-cols-5 gap-1.5 text-[10px] text-center font-mono">
              <div class="h-10 rounded bg-primary-100 flex items-end justify-center p-1 text-slate-800">100</div>
              <div class="h-10 rounded bg-primary-300 flex items-end justify-center p-1 text-slate-800">300</div>
              <div class="h-10 rounded bg-primary-500 flex items-end justify-center p-1 text-white">500</div>
              <div class="h-10 rounded bg-primary-600 flex items-end justify-center p-1 text-white ring-2 ring-primary-400">600</div>
              <div class="h-10 rounded bg-primary-800 flex items-end justify-center p-1 text-white">800</div>
            </div>
          </div>

          <!-- Accent Teal -->
          <div class="card p-4 space-y-3">
            <div class="text-sm font-semibold">Accent (Teal #14B8A6 - Live)</div>
            <div class="grid grid-cols-5 gap-1.5 text-[10px] text-center font-mono">
              <div class="h-10 rounded bg-accent-100 flex items-end justify-center p-1 text-slate-800">100</div>
              <div class="h-10 rounded bg-accent-300 flex items-end justify-center p-1 text-slate-800">300</div>
              <div class="h-10 rounded bg-accent-500 flex items-end justify-center p-1 text-white ring-2 ring-accent-400">500</div>
              <div class="h-10 rounded bg-accent-700 flex items-end justify-center p-1 text-white">700</div>
              <div class="h-10 rounded bg-accent-900 flex items-end justify-center p-1 text-white">900</div>
            </div>
          </div>

          <!-- Semantic States -->
          <div class="card p-4 space-y-3">
            <div class="text-sm font-semibold">Semantic Functional Scales</div>
            <div class="grid grid-cols-4 gap-1.5 text-[10px] text-center font-mono text-white">
              <div class="h-10 rounded bg-emerald-500 flex items-end justify-center p-1">Success</div>
              <div class="h-10 rounded bg-sky-500 flex items-end justify-center p-1">Info</div>
              <div class="h-10 rounded bg-amber-500 flex items-end justify-center p-1">Warn</div>
              <div class="h-10 rounded bg-rose-500 flex items-end justify-center p-1">Danger</div>
            </div>
          </div>

          <!-- Semantic Aliases -->
          <div class="card p-4 space-y-2 text-xs">
            <div class="font-semibold text-sm mb-1">Semantic Aliases</div>
            <div class="flex items-center justify-between p-1.5 rounded bg-subtle border border-border-default">
              <span>--bg-subtle</span>
              <span class="font-mono text-secondary">Table Header / Hover</span>
            </div>
            <div class="flex items-center justify-between p-1.5 rounded bg-muted">
              <span>--bg-muted</span>
              <span class="font-mono text-secondary">Disabled / Skeletons</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Typography System -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold">🔤 Typography & Numbers (Inter Variable + JetBrains Mono)</h2>
        <div class="card p-6 divide-y divide-border-default space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-4 items-center gap-4 pt-3 first:pt-0">
            <span class="text-xs font-mono text-secondary">text-3xl (30px / 36px)</span>
            <div class="md:col-span-3 text-3xl font-semibold tracking-tight">AED 1,489,230.50 <span class="text-sm font-normal text-muted tabular-nums">· tabular-nums</span></div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-4 items-center gap-4 pt-4">
            <span class="text-xs font-mono text-secondary">text-2xl (24px / 32px)</span>
            <div class="md:col-span-3 text-2xl font-semibold">Orders & Dispatch Cockpit</div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-4 items-center gap-4 pt-4">
            <span class="text-xs font-mono text-secondary">text-base & Mono IDs</span>
            <div class="md:col-span-3 flex flex-wrap items-center gap-3 text-base">
              <span>Standard body text with monospace IDs:</span>
              <code class="px-2 py-0.5 rounded bg-subtle border border-border-strong font-mono text-sm font-medium">ORD-2026-9041</code>
              <code class="px-2 py-0.5 rounded bg-subtle border border-border-strong font-mono text-sm font-medium">DXB-77291-C</code>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-4 items-center gap-4 pt-4">
            <span class="text-xs font-mono text-secondary">Tabular Alignment</span>
            <div class="md:col-span-3 grid grid-cols-3 max-w-sm font-mono text-sm tabular-nums">
              <span>11,111.11 kg</span>
              <span>88,888.88 kg</span>
              <span>99,999.99 kg</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Status Vocabulary Showcase -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold">🏷️ Status Vocabulary (All 38 Registered Statuses)</h2>
        <div class="card p-6">
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <div
              v-for="(meta, key) in STATUS_MAP"
              :key="key"
              :class="[
                'flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium transition-transform hover:scale-[1.02]',
                TONE_STYLES[meta.tone]?.bg,
                TONE_STYLES[meta.tone]?.text,
                TONE_STYLES[meta.tone]?.border,
              ]"
            >
              <span
                :class="[
                  'w-2 h-2 rounded-full shrink-0',
                  TONE_STYLES[meta.tone]?.dot,
                  meta.pulse && 'animate-ping opacity-75'
                ]"
              />
              <span class="truncate">{{ meta.label }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Elevations & Shadows -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold">Layers, Radius & Elevation</h2>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div class="card p-4 shadow-xs text-center text-xs font-medium">shadow-xs<br><span class="text-muted text-[11px]">Subtle cards</span></div>
          <div class="card p-4 shadow-sm text-center text-xs font-medium">shadow-sm<br><span class="text-muted text-[11px]">Hover cards</span></div>
          <div class="card p-4 shadow-md text-center text-xs font-medium">shadow-md<br><span class="text-muted text-[11px]">Dropdowns</span></div>
          <div class="card p-4 shadow-lg text-center text-xs font-medium">shadow-lg<br><span class="text-muted text-[11px]">Popovers</span></div>
          <div class="card p-4 shadow-xl text-center text-xs font-medium col-span-2 md:col-span-1">shadow-xl<br><span class="text-muted text-[11px]">Modals</span></div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { Sun, Moon, Monitor } from 'lucide-vue-next'
import { useTheme } from '../composables/useTheme'
import { STATUS_MAP, TONE_STYLES } from '../design/status'

const { theme, setTheme } = useTheme()

function modeIcon(mode) {
  if (mode === 'light') return Sun
  if (mode === 'dark') return Moon
  return Monitor
}
</script>
