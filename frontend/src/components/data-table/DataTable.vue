<template>
  <!--
    The table fills its parent (flex-1) and owns the only scroll container,
    so the header stays pinned vertically and the selection + actions columns
    stay pinned horizontally while the page itself never scrolls.
  -->
  <div class="relative flex min-h-0 flex-1 flex-col">
    <!-- Background refetch indicator -->
    <div v-if="isFetching && rows.length" class="pointer-events-none absolute inset-x-0 top-0 z-40 h-0.5 overflow-hidden">
      <div class="h-full w-1/3 animate-[aow-progress_1.1s_ease-in-out_infinite] rounded-full bg-primary-500" />
    </div>

    <!-- Error -->
    <div v-if="error" class="flex flex-1 flex-col items-center justify-center gap-3 p-10 text-center">
      <div class="flex h-11 w-11 items-center justify-center rounded-full bg-danger-50 text-danger-600 dark:bg-danger-500/10 dark:text-danger-500">
        <AlertTriangle class="h-5 w-5" />
      </div>
      <div>
        <h4 class="text-sm font-semibold text-primary">Couldn't load records</h4>
        <p class="mx-auto mt-1 max-w-md text-xs text-muted">{{ error }}</p>
      </div>
      <Button variant="outline" size="sm" @click="$emit('retry')">
        <RotateCcw class="h-3.5 w-3.5" />
        Try again
      </Button>
    </div>

    <div
      v-else
      ref="scrollRef"
      class="relative min-h-0 flex-1 overflow-auto overscroll-contain focus:outline-none"
      tabindex="0"
      role="grid"
      :aria-rowcount="rows.length"
      :aria-busy="loading || isFetching"
      @scroll.passive="updateScrollShadows"
      @keydown="onKeydown"
    >
      <table
        class="table-fixed border-separate border-spacing-0 text-left text-[13px]"
        :style="{ width: `${tableWidth}px`, minWidth: '100%' }"
      >
        <colgroup>
          <col v-if="enableSelection" :style="{ width: `${SELECT_W}px` }" />
          <col v-for="col in visibleColumns" :key="col.name" :style="{ width: `${widthOf(col)}px` }" />
          <col />
          <col v-if="enableActions" :style="{ width: `${actionsWidth}px` }" />
        </colgroup>

        <thead>
          <tr>
            <th
              v-if="enableSelection"
              scope="col"
              :class="cn(headCell, 'left-0 z-30 px-0', scrolledX && leftShadow)"
            >
              <div class="flex items-center justify-center">
                <Checkbox
                  :model-value="isPagePartiallySelected ? 'indeterminate' : isPageSelected"
                  :disabled="!rows.length"
                  aria-label="Select all rows on this page"
                  @update:model-value="$emit('select-all', Boolean($event))"
                />
              </div>
            </th>

            <th
              v-for="col in visibleColumns"
              :key="col.name"
              scope="col"
              :aria-sort="ariaSort(col.name)"
              :class="cn(
                headCell,
                'group/th z-20 px-0',
                resizing === col.name && 'bg-slate-100 dark:bg-slate-800'
              )"
            >
              <button
                v-if="col.sortable !== false"
                type="button"
                :class="cn(
                  'flex h-full w-full items-center gap-1.5 px-3 py-2.5 text-left transition-colors hover:bg-slate-100 hover:text-primary dark:hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary-500/50',
                  col.align === 'right' && 'flex-row-reverse text-right',
                  sortDir(col.name) && 'text-primary'
                )"
                :title="`Sort by ${col.label}`"
                @click="onHeaderClick(col)"
              >
                <span class="truncate">{{ col.label }}</span>
                <ArrowUp v-if="sortDir(col.name) === 'asc'" class="h-3.5 w-3.5 shrink-0 text-primary-600 dark:text-primary-400" />
                <ArrowDown v-else-if="sortDir(col.name) === 'desc'" class="h-3.5 w-3.5 shrink-0 text-primary-600 dark:text-primary-400" />
                <ChevronsUpDown v-else class="h-3.5 w-3.5 shrink-0 opacity-0 transition-opacity group-hover/th:opacity-60" />
              </button>
              <div
                v-else
                :class="cn('flex items-center px-3 py-2.5', col.align === 'right' && 'justify-end')"
              >
                <span class="truncate">{{ col.label }}</span>
              </div>

              <!-- Resize handle: drag to resize, double-click to reset -->
              <div
                role="separator"
                aria-orientation="vertical"
                :aria-label="`Resize ${col.label} column`"
                :class="cn(
                  'absolute right-0 top-0 z-10 flex h-full w-2.5 cursor-col-resize touch-none select-none justify-end',
                  'before:my-2 before:w-[2px] before:rounded-full before:transition-colors',
                  resizing === col.name ? 'before:bg-primary-500' : 'before:bg-border-strong group-hover/th:before:bg-border-strong hover:before:!bg-primary-400'
                )"
                title="Drag to resize · double-click to reset"
                @pointerdown.stop.prevent="startResize(col, $event)"
                @click.stop
                @dblclick.stop="resetWidth(col)"
              />
            </th>

            <!-- Filler absorbs spare width so explicit column widths are respected -->
            <th :class="cn(headCell, 'z-20 p-0')" aria-hidden="true" />

            <th
              v-if="enableActions"
              scope="col"
              :class="cn(headCell, 'right-0 z-30 px-3 text-right', overflowRight && rightShadow)"
            >
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- Initial loading skeleton -->
          <template v-if="loading && !rows.length">
            <tr v-for="n in skeletonRows" :key="`sk-${n}`">
              <td v-if="enableSelection" :class="cn(bodyCell, densityClass, 'sticky left-0 z-10 bg-surface')">
                <div class="mx-auto h-4 w-4 animate-pulse rounded bg-muted" />
              </td>
              <td v-for="col in visibleColumns" :key="col.name" :class="cn(bodyCell, densityClass, 'bg-surface px-3')">
                <div class="h-3.5 animate-pulse rounded bg-muted" :style="{ width: `${35 + ((n * 17 + col.name.length * 7) % 50)}%` }" />
              </td>
              <td :class="cn(bodyCell, 'bg-surface')" />
              <td v-if="enableActions" :class="cn(bodyCell, densityClass, 'sticky right-0 z-10 bg-surface px-3')">
                <div class="ml-auto h-4 w-10 animate-pulse rounded bg-muted" />
              </td>
            </tr>
          </template>

          <template v-else>
            <tr
              v-for="(row, idx) in rows"
              :key="row.id ?? idx"
              :data-row="idx"
              :aria-selected="isSelected(row)"
              :class="cn('group cursor-pointer transition-opacity', isFetching && 'opacity-60')"
              @click="onRowClick(row, $event)"
              @auxclick="onRowAuxClick(row, $event)"
            >
              <td
                v-if="enableSelection"
                :class="cn(bodyCell, densityClass, rowBg(row, idx), 'sticky left-0 z-10 px-0', scrolledX && leftShadow)"
                @click.stop="$emit('toggle-select', row.id)"
              >
                <div class="flex items-center justify-center">
                  <Checkbox
                    :model-value="isSelected(row)"
                    :aria-label="`Select row ${row.number || row.code || row.id}`"
                    @update:model-value="$emit('toggle-select', row.id)"
                  />
                </div>
              </td>

              <td
                v-for="col in visibleColumns"
                :key="col.name"
                :class="cn(
                  bodyCell,
                  densityClass,
                  rowBg(row, idx),
                  'overflow-hidden text-ellipsis whitespace-nowrap px-3 text-primary',
                  col.align === 'right' && 'text-right tabular-nums'
                )"
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

              <td :class="cn(bodyCell, rowBg(row, idx))" />

              <td
                v-if="enableActions"
                :class="cn(bodyCell, densityClass, rowBg(row, idx), 'sticky right-0 z-10 px-2', overflowRight && rightShadow)"
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

      <!-- Empty state sits below the sticky header, centred in the viewport -->
      <div
        v-if="!loading && !rows.length"
        class="sticky left-0 flex min-h-[260px] items-center justify-center p-8"
        :style="{ width: viewportWidth ? `${viewportWidth}px` : '100%' }"
      >
        <EmptyState
          :variant="hasFilters ? 'no-results' : 'no-data'"
          :default-actions="false"
          :title="hasFilters ? 'No matching records' : `No ${resourceTitle.toLowerCase()} yet`"
          :description="hasFilters ? 'Try adjusting your search or filters.' : `Records you create will appear here.`"
          :action-label="hasFilters ? 'Clear filters' : (meta?.create ? `Create ${singular}` : undefined)"
          @action="hasFilters ? $emit('clear-filters') : $emit('create')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ArrowUp, ArrowDown, ChevronsUpDown, AlertTriangle, RotateCcw } from 'lucide-vue-next'
import { useResizeObserver } from '@vueuse/core'
import CellDispatcher from './cells/CellDispatcher.vue'
import ActionsCell from './cells/ActionsCell.vue'
import EmptyState from '../feedback/EmptyState.vue'
import Button from '../ui/Button.vue'
import Checkbox from '../ui/Checkbox.vue'
import { cn } from '../../utils/cn'

const props = defineProps({
  rows: { type: Array, default: () => [] },
  columns: { type: Array, required: true }, // [{ name, label, sortable, align, width, minWidth }]
  fields: { type: Object, default: () => ({}) },
  resourceKey: { type: String, required: true },
  resourceTitle: { type: String, default: 'Records' },
  meta: Object,
  hiddenColumns: { type: Array, default: () => [] },
  columnOrder: { type: Array, default: () => [] },
  columnWidths: { type: Object, default: () => ({}) },
  ordering: { type: String, default: '' },
  selectedRowIds: { type: Array, default: () => [] },
  isPageSelected: { type: Boolean, default: false },
  isPagePartiallySelected: { type: Boolean, default: false },
  density: {
    type: String,
    default: 'normal',
    validator: (v) => ['compact', 'normal', 'relaxed'].includes(v),
  },
  loading: { type: Boolean, default: false },
  isFetching: { type: Boolean, default: false },
  error: { type: String, default: '' },
  pageSize: { type: Number, default: 20 },
  hasFilters: { type: Boolean, default: false },
  enableSelection: { type: Boolean, default: true },
  enableActions: { type: Boolean, default: true },
  customActions: { type: Array, default: () => [] },
})

const emit = defineEmits([
  'sort', 'row-click', 'row-open-new-tab', 'toggle-select', 'select-all', 'clear-filters',
  'create', 'retry', 'resize-column', 'view', 'edit', 'duplicate', 'delete', 'action',
])

const SELECT_W = 44
const DEFAULT_W = 160
const MIN_W = 72

const scrollRef = ref(null)
const focusedIndex = ref(-1)
const scrolledX = ref(false)
const overflowRight = ref(false)
const viewportWidth = ref(0)

const headCell =
  'sticky top-0 border-b border-border-default bg-slate-50 text-[11px] font-semibold uppercase tracking-wide text-muted whitespace-nowrap dark:bg-slate-900 select-none'
const bodyCell = 'border-b border-border-default/70 align-middle transition-colors'
const leftShadow = 'shadow-[1px_0_0_rgb(var(--border-default)),6px_0_10px_-4px_rgb(15_23_42/0.12)] dark:shadow-[1px_0_0_rgb(var(--border-default)),6px_0_10px_-4px_rgb(0_0_0/0.5)]'
const rightShadow = 'shadow-[-1px_0_0_rgb(var(--border-default)),-6px_0_10px_-4px_rgb(15_23_42/0.12)] dark:shadow-[-1px_0_0_rgb(var(--border-default)),-6px_0_10px_-4px_rgb(0_0_0/0.5)]'

const canEdit = computed(() => props.meta?.create !== false && !props.meta?.readonly)
const actionsWidth = computed(() => (canEdit.value ? 92 : 60))

const singular = computed(() => {
  const t = (props.resourceTitle || 'record').toLowerCase()
  return t.endsWith('ies') ? `${t.slice(0, -3)}y` : t.endsWith('s') ? t.slice(0, -1) : t
})

const visibleColumns = computed(() => {
  const hidden = new Set(props.hiddenColumns)
  let cols = props.columns.filter((c) => !hidden.has(c.name))
  if (props.columnOrder?.length) {
    const order = new Map(props.columnOrder.map((n, i) => [n, i]))
    cols = [...cols].sort((a, b) => (order.get(a.name) ?? 999) - (order.get(b.name) ?? 999))
  }
  return cols
})

// Live widths while dragging, so we don't persist on every mousemove.
const liveWidths = reactive({})
const resizing = ref(null)

function widthOf(col) {
  return liveWidths[col.name] ?? props.columnWidths[col.name] ?? col.width ?? DEFAULT_W
}

const tableWidth = computed(() => {
  let w = visibleColumns.value.reduce((sum, c) => sum + widthOf(c), 0)
  if (props.enableSelection) w += SELECT_W
  if (props.enableActions) w += actionsWidth.value
  return w
})

const densityClass = computed(() => ({
  compact: 'h-9 py-1',
  normal: 'h-11 py-2',
  relaxed: 'h-14 py-3',
}[props.density]))

const skeletonRows = computed(() => Math.min(props.pageSize || 10, 12))

const selectedSet = computed(() => new Set(props.selectedRowIds))
const isSelected = (row) => selectedSet.value.has(row.id)

function rowBg(row, idx) {
  if (isSelected(row)) {
    return 'bg-primary-50 group-hover:bg-primary-100 dark:bg-primary-950 dark:group-hover:bg-primary-900'
  }
  if (idx === focusedIndex.value) {
    return 'bg-slate-100 dark:bg-slate-800'
  }
  return 'bg-surface group-hover:bg-slate-50 dark:group-hover:bg-slate-800'
}

// ---------- Sorting ----------
function sortDir(name) {
  if (props.ordering === name) return 'asc'
  if (props.ordering === `-${name}`) return 'desc'
  return null
}

function ariaSort(name) {
  const d = sortDir(name)
  return d === 'asc' ? 'ascending' : d === 'desc' ? 'descending' : 'none'
}

let suppressHeaderClick = false
function onHeaderClick(col) {
  if (suppressHeaderClick) return
  emit('sort', col.name)
}

// ---------- Resizing ----------
let resizeState = null

function startResize(col, event) {
  const th = event.currentTarget.parentElement
  const startWidth = th?.getBoundingClientRect().width || widthOf(col)
  resizeState = {
    col,
    startX: event.clientX,
    startWidth,
    min: col.minWidth || MIN_W,
    pointerId: event.pointerId,
    target: event.currentTarget,
  }
  resizing.value = col.name
  liveWidths[col.name] = Math.round(startWidth)
  event.currentTarget.setPointerCapture?.(event.pointerId)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  window.addEventListener('pointermove', onResizeMove)
  window.addEventListener('pointerup', stopResize)
  window.addEventListener('pointercancel', stopResize)
}

function onResizeMove(event) {
  if (!resizeState) return
  const next = Math.max(resizeState.min, Math.min(900, resizeState.startWidth + event.clientX - resizeState.startX))
  liveWidths[resizeState.col.name] = Math.round(next)
}

function stopResize() {
  if (!resizeState) return
  const { col, target, pointerId } = resizeState
  const finalWidth = liveWidths[col.name]
  try { target.releasePointerCapture?.(pointerId) } catch {}
  resizeState = null
  resizing.value = null
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
  window.removeEventListener('pointermove', onResizeMove)
  window.removeEventListener('pointerup', stopResize)
  window.removeEventListener('pointercancel', stopResize)

  suppressHeaderClick = true
  setTimeout(() => { suppressHeaderClick = false }, 0)

  emit('resize-column', { column: col.name, width: finalWidth })
  // Drop the live override once the persisted width comes back as a prop.
  nextTick(() => { delete liveWidths[col.name] })
  nextTick(updateScrollShadows)
}

function resetWidth(col) {
  delete liveWidths[col.name]
  emit('resize-column', { column: col.name, width: null })
  nextTick(updateScrollShadows)
}

// ---------- Scroll shadows ----------
function updateScrollShadows() {
  const el = scrollRef.value
  if (!el) return
  scrolledX.value = el.scrollLeft > 0
  overflowRight.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 1
  viewportWidth.value = el.clientWidth
}

useResizeObserver(scrollRef, updateScrollShadows)
watch(tableWidth, () => nextTick(updateScrollShadows))

// New page of data → back to the top of the list.
watch(
  () => props.rows,
  (next, prev) => {
    focusedIndex.value = -1
    if (prev && next !== prev && scrollRef.value) scrollRef.value.scrollTop = 0
  }
)

// ---------- Row interaction ----------
function onRowClick(row, event) {
  if (window.getSelection?.()?.toString()) return // allow copying text from a cell
  if (event.metaKey || event.ctrlKey) emit('row-open-new-tab', row)
  else emit('row-click', row)
}

function onRowAuxClick(row, event) {
  if (event.button === 1) emit('row-open-new-tab', row)
}

function focusRow(idx) {
  focusedIndex.value = idx
  nextTick(() => {
    scrollRef.value?.querySelector(`[data-row="${idx}"]`)?.scrollIntoView({ block: 'nearest' })
  })
}

function onKeydown(e) {
  if (e.target !== scrollRef.value || !props.rows.length) return
  const last = props.rows.length - 1
  switch (e.key) {
    case 'ArrowDown':
    case 'j':
      e.preventDefault()
      focusRow(Math.min(last, focusedIndex.value + 1))
      break
    case 'ArrowUp':
    case 'k':
      e.preventDefault()
      focusRow(Math.max(0, focusedIndex.value - 1))
      break
    case 'Home':
      e.preventDefault()
      focusRow(0)
      break
    case 'End':
      e.preventDefault()
      focusRow(last)
      break
    case 'Enter':
      if (focusedIndex.value >= 0) {
        e.preventDefault()
        emit('row-click', props.rows[focusedIndex.value])
      }
      break
    case ' ':
    case 'x':
      if (focusedIndex.value >= 0 && props.enableSelection) {
        e.preventDefault()
        emit('toggle-select', props.rows[focusedIndex.value].id)
      }
      break
  }
}

onMounted(() => nextTick(updateScrollShadows))
onBeforeUnmount(() => {
  if (resizeState) stopResize()
})
</script>

<style>
@keyframes aow-progress {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(300%); }
}
</style>
