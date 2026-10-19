<template>
  <div class="relative w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs overflow-hidden">
    <!-- Top Progress Indicator for Background Refetch -->
    <div
      v-if="isFetching"
      class="absolute top-0 left-0 right-0 h-0.5 bg-brand-500 overflow-hidden z-30"
    >
      <div class="h-full w-full bg-brand-400 origin-left animate-pulse" />
    </div>

    <!-- Error State -->
    <div v-if="error" class="p-8 text-center space-y-3">
      <div class="inline-flex items-center justify-center h-10 w-10 rounded-full bg-rose-50 text-rose-600 dark:bg-rose-950/50 dark:text-rose-400">
        <AlertTriangle class="h-5 w-5" />
      </div>
      <div>
        <h4 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Failed to load records</h4>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-md mx-auto">{{ error }}</p>
      </div>
      <Button variant="outline" size="sm" @click="$emit('retry')">
        <RotateCcw class="w-3.5 h-3.5 mr-1.5" />
        Retry
      </Button>
    </div>

    <!-- Table Container with Horizontal Scroll -->
    <div
      v-else
      ref="tableContainerRef"
      class="overflow-x-auto relative max-w-full"
      tabindex="0"
      @keydown.down.prevent="moveFocus(1)"
      @keydown.up.prevent="moveFocus(-1)"
      @keydown.enter.prevent="onEnterKey"
      @keydown.space.prevent="onSpaceKey"
    >
      <table class="w-full text-left border-collapse select-none">
        <!-- Table Header -->
        <thead class="sticky top-0 z-20 bg-slate-50/95 dark:bg-slate-950/95 backdrop-blur-xs border-b border-slate-200 dark:border-slate-800 text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          <tr>
            <!-- Selection Checkbox Column (Sticky Left) -->
            <th
              v-if="enableSelection"
              class="sticky left-0 z-20 bg-slate-50/95 dark:bg-slate-950/95 w-10 px-3 py-3 border-r border-slate-200 dark:border-slate-800 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.06)] dark:shadow-[2px_0_5px_-2px_rgba(0,0,0,0.4)]"
            >
              <div class="flex items-center justify-center">
                <input
                  type="checkbox"
                  :checked="isPageSelected"
                  :indeterminate="isPagePartiallySelected"
                  class="rounded border-slate-300 text-brand-600 focus:ring-brand-500 h-3.5 w-3.5 cursor-pointer"
                  @change="$emit('select-all', $event.target.checked)"
                />
              </div>
            </th>

            <!-- Data Columns -->
            <th
              v-for="col in visibleColumns"
              :key="col.name"
              :style="{ width: columnWidths[col.name] ? `${columnWidths[col.name]}px` : undefined }"
              :class="[
                'relative px-3 py-3 font-semibold transition-colors',
                col.sortable !== false ? 'cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-900 select-none' : '',
                col.align === 'right' ? 'text-right' : 'text-left'
              ]"
              :aria-sort="getAriaSort(col.name)"
              @click="col.sortable !== false && $emit('sort', col.name)"
            >
              <div :class="['inline-flex items-center gap-1.5 max-w-full', col.align === 'right' && 'justify-end w-full']">
                <span class="truncate">{{ col.label }}</span>
                <span v-if="col.sortable !== false" class="text-slate-400">
                  <ArrowUp v-if="ordering === col.name" class="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
                  <ArrowDown v-else-if="ordering === '-' + col.name" class="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
                  <ArrowUpDown v-else class="w-3 h-3 opacity-0 group-hover:opacity-100 hover:opacity-100 text-slate-400 transition-opacity" />
                </span>
              </div>

              <!-- Resize Handle -->
              <div
                class="absolute right-0 top-0 bottom-0 w-1 hover:w-1.5 hover:bg-brand-500 cursor-col-resize select-none"
                @mousedown.stop.prevent="startResize(col.name, $event)"
              />
            </th>

            <!-- Actions Column (Sticky Right) -->
            <th
              v-if="enableActions"
              class="sticky right-0 z-20 bg-slate-50/95 dark:bg-slate-950/95 w-12 px-3 py-3 text-right border-l border-slate-200 dark:border-slate-800 shadow-[-2px_0_5px_-2px_rgba(0,0,0,0.06)] dark:shadow-[-2px_0_5px_-2px_rgba(0,0,0,0.4)]"
            >
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>

        <!-- Table Body -->
        <tbody class="divide-y divide-slate-100 dark:divide-slate-800/60 text-xs">
          <!-- Initial Loading Skeletons -->
          <template v-if="loading && rows.length === 0">
            <tr v-for="n in pageSize" :key="n" class="animate-pulse">
              <td v-if="enableSelection" class="sticky left-0 bg-white dark:bg-slate-900 px-3 py-3 border-r border-slate-100 dark:border-slate-800">
                <div class="h-3.5 w-3.5 rounded bg-slate-200 dark:bg-slate-800 mx-auto" />
              </td>
              <td v-for="col in visibleColumns" :key="col.name" :class="[densityClass, 'px-3']">
                <div class="h-3.5 rounded bg-slate-200 dark:bg-slate-800" :style="{ width: `${40 + (n * 13) % 45}%` }" />
              </td>
              <td v-if="enableActions" class="sticky right-0 bg-white dark:bg-slate-900 px-3 py-3 border-l border-slate-100 dark:border-slate-800">
                <div class="h-4 w-4 rounded-full bg-slate-200 dark:bg-slate-800 ml-auto" />
              </td>
            </tr>
          </template>

          <!-- Actual Rows -->
          <template v-else-if="rows.length > 0">
            <tr
              v-for="(row, idx) in rows"
              :key="row.id || idx"
              :class="[
                'group transition-colors cursor-pointer',
                selectedRowIds.includes(row.id)
                  ? 'bg-brand-50/60 dark:bg-brand-950/30'
                  : idx === focusedIndex
                    ? 'bg-slate-100 dark:bg-slate-800/80 ring-1 ring-inset ring-brand-500/30'
                    : 'hover:bg-slate-50 dark:hover:bg-slate-800/50',
                isFetching ? 'opacity-70' : 'opacity-100'
              ]"
              @click="onRowClick(row, $event)"
            >
              <!-- Selection Checkbox (Sticky Left) -->
              <td
                v-if="enableSelection"
                class="sticky left-0 z-10 w-10 px-3 py-2.5 bg-inherit border-r border-slate-100 dark:border-slate-800 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.06)] dark:shadow-[2px_0_5px_-2px_rgba(0,0,0,0.4)]"
                @click.stop
              >
                <div class="flex items-center justify-center">
                  <input
                    type="checkbox"
                    :checked="selectedRowIds.includes(row.id)"
                    class="rounded border-slate-300 text-brand-600 focus:ring-brand-500 h-3.5 w-3.5 cursor-pointer"
                    @change="$emit('toggle-select', row.id)"
                  />
                </div>
              </td>

              <!-- Data Cells -->
              <td
                v-for="col in visibleColumns"
                :key="col.name"
                :class="[
                  densityClass,
                  'px-3 text-slate-800 dark:text-slate-200',
                  col.align === 'right' ? 'text-right' : 'text-left'
                ]"
              >
                <slot :name="`cell-${col.name}`" :row="row" :column="col">
                  <CellDispatcher
                    :row="row"
                    :name="col.name"
                    :field="fields[col.name]"
                    :resource-key="resourceKey"
                  />
                </slot>
              </td>

              <!-- Actions Kebab (Sticky Right) -->
              <td
                v-if="enableActions"
                class="sticky right-0 z-10 w-12 px-3 py-2 bg-inherit border-l border-slate-100 dark:border-slate-800 shadow-[-2px_0_5px_-2px_rgba(0,0,0,0.06)] dark:shadow-[-2px_0_5px_-2px_rgba(0,0,0,0.4)]"
                @click.stop
              >
                <ActionsCell
                  :row="row"
                  :resource-key="resourceKey"
                  :meta="meta"
                  :custom-actions="customActions"
                  @view="$emit('view', row)"
                  @edit="$emit('edit', row)"
                  @duplicate="$emit('duplicate', row)"
                  @delete="$emit('delete', row)"
                  @action="$emit('action', $event)"
                />
              </td>
            </tr>
          </template>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="!loading && rows.length === 0" class="p-12 text-center">
        <EmptyState
          :title="hasFilters ? 'No matching records' : `No ${resourceTitle.toLowerCase()} yet`"
          :description="hasFilters ? 'Try adjusting or clearing your search and filters to find records.' : `Get started by creating your first ${resourceTitle.toLowerCase().slice(0, -1)}.`"
          :action-label="hasFilters ? 'Clear filters' : (meta?.create ? 'Create first record' : undefined)"
          @action="hasFilters ? $emit('clear-filters') : $emit('create')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowUp, ArrowDown, ArrowUpDown, AlertTriangle, RotateCcw } from 'lucide-vue-next'
import CellDispatcher from './cells/CellDispatcher.vue'
import ActionsCell from './cells/ActionsCell.vue'
import EmptyState from '../feedback/EmptyState.vue'
import Button from '../ui/Button.vue'

const props = defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
  columns: {
    type: Array,
    required: true, // Array<{ name, label, sortable, align }>
  },
  fields: {
    type: Object,
    default: () => ({}),
  },
  resourceKey: {
    type: String,
    required: true,
  },
  resourceTitle: {
    type: String,
    default: 'Records',
  },
  meta: Object,
  hiddenColumns: {
    type: Array,
    default: () => [],
  },
  columnOrder: {
    type: Array,
    default: () => [],
  },
  columnWidths: {
    type: Object,
    default: () => ({}),
  },
  ordering: {
    type: String,
    default: '',
  },
  selectedRowIds: {
    type: Array,
    default: () => [],
  },
  isPageSelected: {
    type: Boolean,
    default: false,
  },
  isPagePartiallySelected: {
    type: Boolean,
    default: false,
  },
  density: {
    type: String,
    default: 'normal',
    validator: (v) => ['compact', 'normal', 'relaxed'].includes(v),
  },
  loading: {
    type: Boolean,
    default: false,
  },
  isFetching: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
  pageSize: {
    type: Number,
    default: 20,
  },
  hasFilters: {
    type: Boolean,
    default: false,
  },
  enableSelection: {
    type: Boolean,
    default: true,
  },
  enableActions: {
    type: Boolean,
    default: true,
  },
  customActions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits([
  'sort',
  'row-click',
  'row-open-new-tab',
  'toggle-select',
  'select-all',
  'clear-filters',
  'create',
  'retry',
  'resize-column',
  'view',
  'edit',
  'duplicate',
  'delete',
  'action',
])

const tableContainerRef = ref(null)
const focusedIndex = ref(-1)

// Column Ordering and Visibility
const visibleColumns = computed(() => {
  const hidden = new Set(props.hiddenColumns)
  let cols = props.columns.filter((c) => !hidden.has(c.name))

  if (props.columnOrder?.length) {
    const orderMap = new Map(props.columnOrder.map((name, i) => [name, i]))
    cols = [...cols].sort((a, b) => {
      const aOrder = orderMap.has(a.name) ? orderMap.get(a.name) : 999
      const bOrder = orderMap.has(b.name) ? orderMap.get(b.name) : 999
      return aOrder - bOrder
    })
  }

  return cols
})

// Density classes
const densityClass = computed(() => {
  if (props.density === 'compact') return 'py-1.5'
  if (props.density === 'relaxed') return 'py-3.5'
  return 'py-2.5'
})

function getAriaSort(colName) {
  if (props.ordering === colName) return 'ascending'
  if (props.ordering === `-${colName}`) return 'descending'
  return 'none'
}

// Row Click Handling (Command/Control click or middle-click)
function onRowClick(row, event) {
  if (event.metaKey || event.ctrlKey || event.button === 1) {
    emit('row-open-new-tab', row)
  } else {
    emit('row-click', row)
  }
}

// Keyboard Navigation
function moveFocus(delta) {
  if (props.rows.length === 0) return
  const next = focusedIndex.value + delta
  if (next >= 0 && next < props.rows.length) {
    focusedIndex.value = next
  }
}

function onEnterKey() {
  if (focusedIndex.value >= 0 && focusedIndex.value < props.rows.length) {
    emit('row-click', props.rows[focusedIndex.value])
  }
}

function onSpaceKey() {
  if (focusedIndex.value >= 0 && focusedIndex.value < props.rows.length) {
    emit('toggle-select', props.rows[focusedIndex.value].id)
  }
}

// Column Resizing via Drag
let activeResizingColumn = null
let startX = 0
let startWidth = 0

function startResize(colName, event) {
  activeResizingColumn = colName
  startX = event.clientX
  startWidth = props.columnWidths[colName] || 150

  window.addEventListener('mousemove', onResizing)
  window.addEventListener('mouseup', stopResize)
}

function onResizing(event) {
  if (!activeResizingColumn) return
  const diff = event.clientX - startX
  const newWidth = Math.max(60, startWidth + diff)
  emit('resize-column', { column: activeResizingColumn, width: newWidth })
}

function stopResize() {
  activeResizingColumn = null
  window.removeEventListener('mousemove', onResizing)
  window.removeEventListener('mouseup', stopResize)
}
</script>
