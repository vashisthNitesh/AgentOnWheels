<template>
  <div class="relative">
    <Popover v-model:open="isOpen" align="end" :side-offset="8" class="w-72 p-0">
      <template #trigger>
        <button
          type="button"
          class="inline-flex items-center gap-1.5 h-8 px-2.5 text-xs font-medium rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-xs"
          title="Customize Columns"
        >
          <SlidersHorizontal class="w-3.5 h-3.5 text-slate-500" />
          <span>Columns</span>
          <span v-if="visibleCount !== totalCount" class="ml-0.5 px-1.5 py-0.2 rounded-full text-[10px] font-semibold bg-brand-50 text-brand-600 dark:bg-brand-950/50 dark:text-brand-400">
            {{ visibleCount }}/{{ totalCount }}
          </span>
        </button>
      </template>

      <div class="p-3 border-b border-slate-100 dark:border-slate-800">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-semibold text-slate-900 dark:text-slate-100">Toggle & Reorder Columns</span>
          <button
            type="button"
            class="text-[11px] font-medium text-brand-600 dark:text-brand-400 hover:underline"
            @click="resetToDefault"
          >
            Reset
          </button>
        </div>
        <div class="relative">
          <Search class="absolute left-2.5 top-2 h-3.5 w-3.5 text-slate-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Search columns…"
            class="w-full pl-8 pr-2.5 py-1 text-xs rounded-md border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
      </div>

      <div ref="sortableContainer" class="max-h-64 overflow-y-auto p-1.5 space-y-0.5 divide-y divide-transparent">
        <div
          v-for="col in filteredColumns"
          :key="col.name"
          :data-id="col.name"
          class="flex items-center justify-between px-2 py-1.5 rounded-md hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors group select-none"
        >
          <label class="flex items-center gap-2 cursor-pointer flex-1 min-w-0 mr-2">
            <input
              type="checkbox"
              :checked="!hiddenColumns.includes(col.name)"
              class="rounded border-slate-300 text-brand-600 focus:ring-brand-500 h-3.5 w-3.5"
              @change="toggleColumn(col.name)"
            />
            <span class="text-xs text-slate-700 dark:text-slate-300 truncate" :title="col.label">
              {{ col.label }}
            </span>
          </label>
          <GripVertical class="drag-handle w-3.5 h-3.5 text-slate-400 opacity-0 group-hover:opacity-100 cursor-grab active:cursor-grabbing flex-shrink-0" />
        </div>
        <div v-if="filteredColumns.length === 0" class="py-4 text-center text-xs text-slate-400">
          No columns found
        </div>
      </div>

      <div class="p-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
        <span>Drag handles to reorder</span>
        <button
          type="button"
          class="text-brand-600 dark:text-brand-400 font-medium hover:underline"
          @click="showAll"
        >
          Show all
        </button>
      </div>
    </Popover>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { SlidersHorizontal, Search, GripVertical } from 'lucide-vue-next'
import Popover from '../ui/Popover.vue'
import Sortable from 'sortablejs'

const props = defineProps({
  columns: {
    type: Array,
    required: true, // Array<{ name: string, label: string }>
  },
  hiddenColumns: {
    type: Array,
    default: () => [],
  },
  columnOrder: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:hiddenColumns', 'update:columnOrder', 'reset'])

const isOpen = ref(false)
const search = ref('')
const sortableContainer = ref(null)
let sortableInstance = null

const totalCount = computed(() => props.columns.length)
const visibleCount = computed(() => props.columns.filter((c) => !props.hiddenColumns.includes(c.name)).length)

// Ordered columns based on columnOrder prop
const orderedColumns = computed(() => {
  if (!props.columnOrder || props.columnOrder.length === 0) return props.columns
  const map = new Map(props.columns.map((c) => [c.name, c]))
  const result = []

  // Add in order
  for (const name of props.columnOrder) {
    if (map.has(name)) {
      result.push(map.get(name))
      map.delete(name)
    }
  }
  // Add any missing
  for (const col of map.values()) {
    result.push(col)
  }
  return result
})

const filteredColumns = computed(() => {
  if (!search.value) return orderedColumns.value
  const q = search.value.toLowerCase()
  return orderedColumns.value.filter(
    (c) => c.label.toLowerCase().includes(q) || c.name.toLowerCase().includes(q)
  )
})

function toggleColumn(name) {
  const next = props.hiddenColumns.includes(name)
    ? props.hiddenColumns.filter((c) => c !== name)
    : [...props.hiddenColumns, name]
  emit('update:hiddenColumns', next)
}

function showAll() {
  emit('update:hiddenColumns', [])
}

function resetToDefault() {
  emit('reset')
}

function initSortable() {
  if (!sortableContainer.value) return
  if (sortableInstance) sortableInstance.destroy()

  sortableInstance = Sortable.create(sortableContainer.value, {
    handle: '.drag-handle',
    animation: 150,
    ghostClass: 'opacity-40',
    onEnd: (evt) => {
      const items = Array.from(sortableContainer.value.children)
      const newOrder = items.map((el) => el.getAttribute('data-id')).filter(Boolean)
      emit('update:columnOrder', newOrder)
    },
  })
}

watch(isOpen, async (val) => {
  if (val) {
    await nextTick()
    initSortable()
  }
})

onMounted(() => {
  if (isOpen.value) initSortable()
})
</script>
