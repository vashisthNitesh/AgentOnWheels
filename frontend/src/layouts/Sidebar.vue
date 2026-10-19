<template>
  <div>
    <!-- Mobile Off-Canvas Drawer Backdrop -->
    <div
      v-if="mobileOpen"
      class="fixed inset-0 z-40 bg-slate-950/50 backdrop-blur-xs lg:hidden transition-opacity"
      @click="$emit('close-mobile')"
    />

    <!-- Sidebar Container -->
    <aside
      :class="cn(
        'fixed inset-y-0 left-0 z-50 flex flex-col bg-surface border-r border-border-default transition-all duration-200 select-none',
        'lg:static lg:z-30',
        collapsed ? 'w-16' : 'w-[248px]',
        mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        $attrs.class
      )"
    >
      <!-- Brand Header -->
      <div class="h-14 flex items-center justify-between px-4 border-b border-border-default shrink-0">
        <router-link
          to="/dashboard"
          class="flex items-center gap-2.5 font-bold text-primary truncate hover:opacity-90 transition"
          @click="$emit('close-mobile')"
        >
          <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center text-white shrink-0 shadow-xs">
            <Truck class="w-4 h-4" />
          </div>
          <span v-if="!collapsed" class="text-sm tracking-tight font-bold font-sans">AgentOnWheels</span>
        </router-link>

        <button
          v-if="mobileOpen"
          type="button"
          class="lg:hidden p-1 rounded-md text-secondary hover:text-primary hover:bg-subtle"
          aria-label="Close sidebar"
          @click="$emit('close-mobile')"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Navigation Items (Scrollable) -->
      <nav class="flex-1 overflow-y-auto px-2 py-3 space-y-6 focus:outline-none">
        <!-- Core Navigation Section -->
        <div class="space-y-1">
          <div v-if="!collapsed" class="px-2.5 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
            Operations
          </div>

          <Tooltip :content="collapsed ? 'Dashboard' : ''" side="right" :disabled="!collapsed">
            <router-link
              to="/dashboard"
              :class="navItemClass('/dashboard')"
              @click="$emit('close-mobile')"
            >
              <LayoutDashboard class="w-4 h-4 shrink-0" />
              <span v-if="!collapsed" class="truncate">Dashboard</span>
            </router-link>
          </Tooltip>

          <Tooltip :content="collapsed ? 'Control tower' : ''" side="right" :disabled="!collapsed">
            <router-link
              to="/control-tower"
              :class="navItemClass('/control-tower')"
              @click="$emit('close-mobile')"
            >
              <Navigation class="w-4 h-4 shrink-0" />
              <span v-if="!collapsed" class="truncate">Control tower</span>
            </router-link>
          </Tooltip>
        </div>

        <!-- Registry Derived Groups -->
        <template v-if="groups">
          <div
            v-for="(items, groupName) in groups"
            :key="groupName"
            class="space-y-1"
          >
            <div v-if="!collapsed" class="px-2.5 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
              {{ groupName }}
            </div>

            <!-- Configuration Hub Link -->
            <template v-if="groupName === 'Configuration'">
              <Tooltip :content="collapsed ? 'Configuration hub' : ''" side="right" :disabled="!collapsed">
                <router-link
                  to="/configuration"
                  :class="navItemClass('/configuration')"
                  @click="$emit('close-mobile')"
                >
                  <Settings class="w-4 h-4 shrink-0" />
                  <span v-if="!collapsed" class="truncate">Configuration hub</span>
                </router-link>
              </Tooltip>
            </template>

            <!-- Standard Group Items -->
            <template v-else>
              <Tooltip
                v-for="item in items"
                :key="item.key"
                :content="collapsed ? item.title : ''"
                side="right"
                :disabled="!collapsed"
              >
                <router-link
                  :to="'/r/' + item.key"
                  :class="navItemClass('/r/' + item.key)"
                  @click="$emit('close-mobile')"
                >
                  <component :is="getModuleIcon(item.key)" class="w-4 h-4 shrink-0" />
                  <span v-if="!collapsed" class="truncate">{{ item.title }}</span>
                </router-link>
              </Tooltip>
            </template>
          </div>
        </template>

        <!-- Skeletons while fetching registry groups -->
        <div v-else class="space-y-2 px-2">
          <div v-for="n in 8" :key="n" class="h-8 bg-muted rounded-md animate-pulse" />
        </div>
      </nav>

      <!-- Sidebar Footer -->
      <div class="p-2 border-t border-border-default bg-subtle/40 shrink-0">
        <button
          type="button"
          class="hidden lg:flex w-full items-center justify-center p-2 rounded-md text-secondary hover:text-primary hover:bg-subtle transition focus-ring"
          :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
          @click="toggleCollapse"
        >
          <ChevronRight v-if="collapsed" class="w-4 h-4" />
          <div v-else class="flex items-center justify-between w-full text-xs font-medium px-1">
            <span>Collapse sidebar</span>
            <ChevronLeft class="w-4 h-4" />
          </div>
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  Truck, LayoutDashboard, Navigation, Settings, ChevronLeft,
  ChevronRight, X
} from 'lucide-vue-next'
import { cn } from '../utils/cn'
import Tooltip from '../components/ui/Tooltip.vue'
import { getModuleIcon } from './moduleIcons'

const props = defineProps({
  groups: {
    type: Object,
    default: null,
  },
  mobileOpen: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['close-mobile'])

const route = useRoute()
const collapsed = ref(false)

onMounted(() => {
  try {
    const saved = localStorage.getItem('aow-sidebar')
    if (saved !== null) {
      collapsed.value = JSON.parse(saved)
    }
  } catch {}
})

function toggleCollapse() {
  collapsed.value = !collapsed.value
  try {
    localStorage.setItem('aow-sidebar', JSON.stringify(collapsed.value))
  } catch {}
}

function navItemClass(path) {
  const isActive = route.path === path || (path !== '/dashboard' && route.path.startsWith(path + '/'))
  return cn(
    'relative flex items-center gap-3 px-2.5 py-2 rounded-md text-xs font-medium transition-all select-none focus-ring',
    isActive
      ? 'bg-primary-50 text-primary-700 font-semibold dark:bg-primary-950/40 dark:text-primary-300 before:absolute before:left-0 before:top-1.5 before:bottom-1.5 before:w-1 before:rounded-r before:bg-primary-600 dark:before:bg-primary-400'
      : 'text-secondary hover:text-primary hover:bg-subtle'
  )
}
</script>
