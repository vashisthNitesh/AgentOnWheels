<template>
  <Popover v-model:open="isOpen" align="end" class="w-72 p-0">
    <template #trigger>
      <button
        type="button"
        class="inline-flex h-9 shrink-0 items-center gap-1.5 rounded-lg border border-border-strong bg-surface px-3 text-[13px] font-medium text-secondary shadow-xs transition-colors hover:bg-subtle hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/40 data-[state=open]:bg-subtle data-[state=open]:text-primary"
        title="Show, hide and reorder columns"
      >
        <Columns3 class="h-4 w-4" />
        <span class="hidden sm:inline">Columns</span>
        <span
          v-if="visibleCount !== totalCount"
          class="rounded-full bg-primary-100 px-1.5 text-[11px] font-semibold leading-[18px] text-primary-700 dark:bg-primary-950 dark:text-primary-300"
        >
          {{ visibleCount }}/{{ totalCount }}
        </span>
      </button>
    </template>

    <div class="border-b border-border-default p-3">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-xs font-semibold text-primary">Columns</span>
        <span class="text-[11px] text-muted">{{ visibleCount }} of {{ totalCount }} shown</span>
      </div>
      <div class="relative">
        <Search class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
        <input
          v-model="search"
          type="text"
          placeholder="Find a column…"
          class="h-8 w-full rounded-md border border-border-strong bg-surface pl-8 pr-2.5 text-xs text-primary outline-none placeholder:text-muted focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15"
        />
      </div>
    </div>

    <div ref="sortableContainer" class="max-h-72 overflow-y-auto p-1">
      <div
        v-for="col in filteredColumns"
        :key="col.name"
        :data-id="col.name"
        class="group flex items-center gap-1 rounded-md pr-1 transition-colors hover:bg-subtle"
      >
        <span
          :class="cn(
            'drag-handle flex h-8 w-6 shrink-0 items-center justify-center text-muted',
            search ? 'cursor-not-allowed opacity-20' : 'cursor-grab opacity-40 group-hover:opacity-100 active:cursor-grabbing'
          )"
          :title="search ? 'Clear the search to reorder' : 'Drag to reorder'"
        >
          <GripVertical class="h-3.5 w-3.5" />
        </span>
        <label class="flex min-w-0 flex-1 cursor-pointer items-center gap-2.5 py-1.5">
          <Checkbox
            :model-value="!hiddenColumns.includes(col.name)"
            :disabled="!hiddenColumns.includes(col.name) && visibleCount <= 1"
            @update:model-value="toggleColumn(col.name)"
          />
          <span class="truncate text-[13px] text-primary" :title="col.label">{{ col.label }}</span>
        </label>
      </div>
      <div v-if="!filteredColumns.length" class="py-6 text-center text-xs text-muted">
        No columns match “{{ search }}”
      </div>
    </div>

    <div class="flex items-center justify-between gap-2 border-t border-border-default bg-subtle/60 px-3 py-2 text-xs">
      <button type="button" class="font-medium text-primary-600 hover:underline dark:text-primary-400" @click="showAll">
        Show all
      </button>
      <button type="button" class="text-secondary hover:text-primary hover:underline" @click="$emit('reset')">
        Reset layout{{ hasCustomWidths ? ' & widths' : '' }}
      </button>
    </div>
  </Popover>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { Columns3, Search, GripVertical } from 'lucide-vue-next'
import Sortable from 'sortablejs'
import Popover from '../ui/Popover.vue'
import Checkbox from '../ui/Checkbox.vue'
import { cn } from '../../utils/cn'

const props = defineProps({
  columns: { type: Array, required: true }, // [{ name, label }]
  hiddenColumns: { type: Array, default: () => [] },
  columnOrder: { type: Array, default: () => [] },
  hasCustomWidths: { type: Boolean, default: false },
})

const emit = defineEmits(['update:hiddenColumns', 'update:columnOrder', 'reset'])

const isOpen = ref(false)
const search = ref('')
const sortableContainer = ref(null)
let sortable = null

const totalCount = computed(() => props.columns.length)
const visibleCount = computed(() => props.columns.filter((c) => !props.hiddenColumns.includes(c.name)).length)

const orderedColumns = computed(() => {
  if (!props.columnOrder?.length) return props.columns
  const map = new Map(props.columns.map((c) => [c.name, c]))
  const result = []
  for (const name of props.columnOrder) {
    if (map.has(name)) {
      result.push(map.get(name))
      map.delete(name)
    }
  }
  return [...result, ...map.values()]
})

const filteredColumns = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return orderedColumns.value
  return orderedColumns.value.filter((c) => c.label.toLowerCase().includes(q) || c.name.toLowerCase().includes(q))
})

function toggleColumn(name) {
  const hidden = props.hiddenColumns.includes(name)
  if (!hidden && visibleCount.value <= 1) return // always keep one column visible
  emit('update:hiddenColumns', hidden ? props.hiddenColumns.filter((c) => c !== name) : [...props.hiddenColumns, name])
}

function showAll() {
  emit('update:hiddenColumns', [])
}

function initSortable(el) {
  sortable?.destroy()
  sortable = null
  if (!el) return
  sortable = Sortable.create(el, {
    handle: '.drag-handle',
    animation: 150,
    ghostClass: 'opacity-40',
    filter: '.cursor-not-allowed',
    onEnd(evt) {
      const { oldIndex, newIndex, item, from } = evt
      if (oldIndex === newIndex || oldIndex == null || newIndex == null) return
      // Undo Sortable's DOM move and let Vue re-render from the new order.
      from.removeChild(item)
      from.insertBefore(item, from.children[oldIndex] || null)
      const names = orderedColumns.value.map((c) => c.name)
      const [moved] = names.splice(oldIndex, 1)
      names.splice(newIndex, 0, moved)
      emit('update:columnOrder', names)
    },
  })
}

// The popover content mounts lazily, so (re)initialise when its list appears.
watch(sortableContainer, (el) => initSortable(el))
watch(search, (q) => sortable?.option('disabled', !!q))
watch(isOpen, (open) => {
  if (!open) search.value = ''
})

onBeforeUnmount(() => sortable?.destroy())
</script>
