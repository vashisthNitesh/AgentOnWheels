<template>
  <header class="sticky top-0 z-topbar h-14 bg-surface/90 backdrop-blur-md border-b border-border-default px-4 flex items-center justify-between gap-3 select-none">
    <!-- Left: Hamburger (mobile) + Breadcrumbs / Title -->
    <div class="flex items-center gap-3 min-w-0">
      <button
        type="button"
        class="lg:hidden p-1.5 rounded-md text-secondary hover:text-primary hover:bg-subtle transition focus-ring"
        aria-label="Open navigation menu"
        @click="$emit('open-mobile')"
      >
        <Menu class="w-5 h-5" />
      </button>

      <div class="hidden sm:flex items-center truncate">
        <span class="text-xs font-semibold text-primary truncate">{{ pageTitle }}</span>
      </div>
    </div>

    <!-- Center / Search Trigger -->
    <div class="flex-1 max-w-md mx-2">
      <button
        type="button"
        class="w-full flex items-center justify-between px-3 py-1.5 rounded-lg border border-border-default bg-subtle/60 text-secondary hover:text-primary hover:border-border-strong text-xs transition shadow-xs focus-ring"
        @click="$emit('open-search')"
      >
        <div class="flex items-center gap-2 truncate">
          <Search class="w-3.5 h-3.5 shrink-0 text-muted" />
          <span class="truncate">Search or jump to…</span>
        </div>
        <div class="flex items-center gap-1 font-mono text-[10px]">
          <Kbd>⌘</Kbd><Kbd>K</Kbd>
        </div>
      </button>
    </div>

    <!-- Right: Clock, Theme, Notifications & User Profile -->
    <div class="flex items-center gap-2 sm:gap-3 shrink-0">
      <!-- Live Clock & Timezone -->
      <span class="hidden md:inline-flex items-center gap-1.5 text-xs text-muted tabular-nums font-mono">
        <Clock class="w-3.5 h-3.5 text-secondary" />
        <span>{{ clock }}</span>
        <span class="text-[11px] text-muted">({{ tzLabel() }})</span>
      </span>

      <!-- Theme Switcher Button -->
      <button
        type="button"
        class="p-1.5 rounded-md text-secondary hover:text-primary hover:bg-subtle transition focus-ring"
        :title="`Current theme: ${theme} (click to toggle)`"
        @click="toggleTheme"
      >
        <Moon v-if="isDark" class="w-4 h-4 text-primary-400" />
        <Sun v-else class="w-4 h-4 text-amber-500" />
      </button>

      <!-- Notifications Bell Popover -->
      <Popover>
        <template #trigger>
          <button
            type="button"
            class="relative p-1.5 rounded-md text-secondary hover:text-primary hover:bg-subtle transition focus-ring"
            aria-label="Notifications"
          >
            <Bell class="w-4 h-4" />
            <span class="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-accent-500 ring-2 ring-surface" />
          </button>
        </template>

        <div class="w-72 space-y-3">
          <div class="flex items-center justify-between border-b border-border-default pb-2">
            <span class="text-xs font-semibold text-primary">Notifications</span>
            <span class="text-[11px] text-primary-600 dark:text-primary-400 cursor-pointer hover:underline">Mark all read</span>
          </div>
          <div class="text-center py-6 text-xs text-muted space-y-1">
            <Bell class="w-6 h-6 mx-auto text-muted/60 mb-2" />
            <p class="font-medium text-primary">All caught up</p>
            <p>No unread dispatch or trip alerts.</p>
          </div>
        </div>
      </Popover>

      <!-- User Profile Menu -->
      <DropdownMenu
        :items="[
          { header: `${auth.user?.name || 'User'} (${auth.user?.username || ''})` },
          { label: auth.user?.is_staff ? 'Staff Administrator' : 'Dispatcher', disabled: true },
          { separator: true },
          { label: 'UI Kit / Design Test Bench', icon: Layers, to: '/ui-kit' },
          { label: 'Configuration Hub', icon: Settings, to: '/configuration' },
          { separator: true },
          { label: 'Sign out', icon: LogOut, danger: true, action: logout },
        ]"
      >
        <template #trigger>
          <button
            type="button"
            class="flex items-center gap-2 p-1 rounded-full hover:bg-subtle transition focus-ring"
          >
            <Avatar :name="auth.user?.name || 'User'" size="28" />
            <span class="hidden xl:inline text-xs font-medium text-primary max-w-[120px] truncate">
              {{ auth.user?.name || 'User' }}
            </span>
          </button>
        </template>
      </DropdownMenu>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  Menu, Search, Bell, Moon, Sun, Clock, LogOut, Settings, Layers
} from 'lucide-vue-next'
import { auth, logout } from '../api'
import { tzLabel } from '../utils/format'
import { useTheme } from '../composables/useTheme'
import Avatar from '../components/ui/Avatar.vue'
import DropdownMenu from '../components/ui/DropdownMenu.vue'
import Popover from '../components/ui/Popover.vue'
import Kbd from '../components/ui/Kbd.vue'

defineEmits(['open-mobile', 'open-search'])

const route = useRoute()
const { theme, isDark, toggleTheme } = useTheme()

const clock = ref('')
let timer

function updateClock() {
  clock.value = new Date().toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: auth.user?.display_tz || 'Asia/Dubai',
  })
}

onMounted(() => {
  updateClock()
  timer = setInterval(updateClock, 15000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const pageTitle = computed(() => {
  const p = route.path
  if (p === '/dashboard') return 'Dashboard'
  if (p === '/control-tower') return 'Control tower'
  if (p === '/configuration') return 'Configuration hub'
  if (p === '/ui-kit') return 'UI Kit & Test Bench'
  if (route.params.key) {
    return route.params.key.replace(/-/g, ' ').replace(/^./, s => s.toUpperCase())
  }
  return 'AgentOnWheels TMS'
})
</script>
