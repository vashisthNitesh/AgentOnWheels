<template>
  <Modal
    v-model:open="isOpen"
    size="md"
    :show-close="false"
    class="!p-0 overflow-hidden"
  >
    <div class="flex flex-col">
      <!-- Search Input Header -->
      <div class="flex items-center gap-3 px-4 py-3.5 border-b border-border-default bg-surface">
        <Search class="w-4 h-4 text-muted shrink-0" />
        <input
          ref="inputRef"
          v-model="query"
          type="text"
          class="w-full bg-transparent text-sm text-primary placeholder:text-muted focus:outline-none"
          placeholder="Search navigation, actions, or order numbers… (Esc to exit)"
          @keydown.down.prevent="navigateHighlight(1)"
          @keydown.up.prevent="navigateHighlight(-1)"
          @keydown.enter.prevent="selectHighlighted"
        />
        <Kbd class="shrink-0">ESC</Kbd>
      </div>

      <!-- Results List -->
      <div class="p-2 max-h-[380px] overflow-y-auto divide-y divide-border-default/50 space-y-2">
        <!-- Empty State -->
        <div v-if="groupedResults.length === 0" class="py-10 text-center text-xs text-muted">
          No matches found for "{{ query }}"
        </div>

        <!-- Groups -->
        <div v-for="group in groupedResults" :key="group.title" class="space-y-1 pt-1 first:pt-0">
          <div class="px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-muted">
            {{ group.title }}
          </div>

          <div
            v-for="item in group.items"
            :key="item.id"
            :class="cn(
              'flex items-center justify-between px-3 py-2 rounded-md text-xs cursor-pointer select-none transition-colors',
              highlightedId === item.id ? 'bg-primary-50 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300 font-medium' : 'hover:bg-subtle text-primary'
            )"
            @mouseenter="highlightedId = item.id"
            @click="executeItem(item)"
          >
            <div class="flex items-center gap-2.5 truncate">
              <component :is="item.icon" class="w-4 h-4 text-secondary shrink-0" />
              <span class="truncate">{{ item.label }}</span>
            </div>
            <span v-if="item.meta" class="font-mono text-[10px] text-muted ml-2">
              {{ item.meta }}
            </span>
          </div>
        </div>
      </div>

      <!-- Footer Info -->
      <div class="px-4 py-2 border-t border-border-default bg-subtle/50 flex items-center justify-between text-[11px] text-muted select-none">
        <div class="flex items-center gap-2">
          <span>Navigate <Kbd>↑</Kbd> <Kbd>↓</Kbd></span>
          <span>Select <Kbd>↵</Kbd></span>
        </div>
        <span>Axle Quick Search</span>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Fuse from 'fuse.js'
import {
  Search, LayoutDashboard, Navigation, Settings, Package, Plus,
  Moon, Sun, LogOut, ArrowRight, Truck, CheckSquare
} from 'lucide-vue-next'
import { useTheme } from '../composables/useTheme'
import { logout } from '../api'
import Modal from '../components/ui/Modal.vue'
import Kbd from '../components/ui/Kbd.vue'
import { cn } from '../utils/cn'

const props = defineProps({
  groups: {
    type: Object,
    default: null,
  },
})

const router = useRouter()
const { isDark, toggleTheme } = useTheme()

const isOpen = ref(false)
const query = ref('')
const inputRef = ref(null)
const highlightedId = ref('')

// Base Actions List
const staticActions = [
  { id: 'act-new-order', group: 'Actions', label: 'Create new order', icon: Plus, action: () => router.push('/r/orders/new') },
  { id: 'act-new-trip', group: 'Actions', label: 'Schedule new trip leg', icon: Plus, action: () => router.push('/r/trips/new') },
  { id: 'act-theme', group: 'Actions', label: 'Toggle dark / light mode', icon: isDark.value ? Sun : Moon, action: () => toggleTheme() },
  { id: 'act-logout', group: 'Actions', label: 'Sign out of workspace', icon: LogOut, action: () => logout() },
]

const navigationItems = computed(() => {
  const items = [
    { id: 'nav-dash', group: 'Navigate', label: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { id: 'nav-tower', group: 'Navigate', label: 'Control tower', icon: Navigation, path: '/control-tower' },
    { id: 'nav-cfg', group: 'Navigate', label: 'Configuration hub', icon: Settings, path: '/configuration' },
    { id: 'nav-uikit', group: 'Navigate', label: 'UI Kit & Test Bench', icon: CheckSquare, path: '/ui-kit' },
  ]

  if (props.groups) {
    for (const [groupName, groupItems] of Object.entries(props.groups)) {
      for (const item of groupItems) {
        items.push({
          id: `nav-${item.key}`,
          group: 'Navigate',
          label: `${item.title} (${groupName})`,
          icon: item.key === 'orders' ? Package : item.key === 'trips' ? Truck : ArrowRight,
          path: `/r/${item.key}`,
        })
      }
    }
  }

  return items
})

const searchablePool = computed(() => {
  return [...navigationItems.value, ...staticActions]
})

const fuse = computed(() => {
  return new Fuse(searchablePool.value, {
    keys: ['label', 'group'],
    threshold: 0.35,
  })
})

const filteredItems = computed(() => {
  if (!query.value.trim()) {
    return searchablePool.value.slice(0, 10)
  }
  return fuse.value.search(query.value).map(res => res.item)
})

const groupedResults = computed(() => {
  const map = {}
  for (const item of filteredItems.value) {
    if (!map[item.group]) map[item.group] = []
    map[item.group].push(item)
  }
  return Object.entries(map).map(([title, items]) => ({ title, items }))
})

watch(filteredItems, (items) => {
  if (items.length > 0) {
    highlightedId.value = items[0].id
  } else {
    highlightedId.value = ''
  }
})

function navigateHighlight(dir) {
  const items = filteredItems.value
  if (!items.length) return
  const currentIdx = items.findIndex(i => i.id === highlightedId.value)
  const nextIdx = (currentIdx + dir + items.length) % items.length
  highlightedId.value = items[nextIdx].id
}

function selectHighlighted() {
  const item = filteredItems.value.find(i => i.id === highlightedId.value)
  if (item) {
    executeItem(item)
  }
}

function executeItem(item) {
  isOpen.value = false
  if (item.action) {
    item.action()
  } else if (item.path) {
    router.push(item.path)
  }
}

function handleGlobalKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    isOpen.value = !isOpen.value
    if (isOpen.value) {
      query.value = ''
      nextTick(() => inputRef.value?.focus())
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})

defineExpose({
  open: () => {
    isOpen.value = true
    query.value = ''
    nextTick(() => inputRef.value?.focus())
  },
})
</script>
