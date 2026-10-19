<template>
  <!-- Loading skeleton before metadata is ready -->
  <div v-if="!meta" class="space-y-4 p-4 sm:p-6 max-w-7xl mx-auto">
    <div class="h-8 w-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
    <div class="h-10 w-full bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
    <div class="h-96 w-full bg-slate-100 dark:bg-slate-900 rounded-lg animate-pulse" />
  </div>

  <!-- Main Resource List View -->
  <div v-else class="space-y-4 p-3 sm:p-6 max-w-7xl mx-auto select-none sm:select-auto">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">{{ meta.icon || '📦' }}</span>
          <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            {{ meta.title }}
          </h1>
          <span v-if="meta.group" class="hidden sm:inline-flex px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider rounded bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
            {{ meta.group }}
          </span>
        </div>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
          <template v-if="loading && rows.length === 0">Loading records…</template>
          <template v-else>
            {{ total.toLocaleString() }} record{{ total === 1 ? '' : 's' }}
            <span v-if="meta.key === 'trips'"> · counts are per leg</span>
          </template>
        </p>
      </div>

      <!-- Header Action Buttons -->
      <div class="flex items-center gap-2">
        <Button
          v-if="meta.create"
          variant="primary"
          size="sm"
          @click="onCreateNew"
        >
          <Plus class="w-4 h-4 mr-1" />
          <span>New {{ singularTitle }}</span>
        </Button>
      </div>
    </div>

    <!-- Toolbar: Search, Status Tabs, Chips, Views, Export, Density -->
    <div class="p-3 sm:p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-3">
      <DataTableToolbar
        :search="search"
        :status="status"
        :status-tabs="statusTabs"
        :counts="counts"
        :active-filters-count="filterComposable.activeCount.value"
        :filter-chips="filterComposable.chips.value"
        :all-columns="allColumns"
        :hidden-columns="hiddenColumns"
        :column-order="columnOrder"
        :density="density"
        :is-fetching="isFetching"
        :is-exporting="csvExport.exporting.value"
        :last-updated="lastUpdated"
        :saved-views="savedViewsComposable.views.value"
        :active-view-id="savedViewsComposable.activeViewId.value"
        :is-view-modified="savedViewsComposable.isModified({ filters: filterComposable.filters.value, ordering, density, search })"
        @update:search="onSearchChange"
        @update:status="onStatusChange"
        @update:hidden-columns="hiddenColumns = $event"
        @update:column-order="columnOrder = $event"
        @update:density="setDensity"
        @open-filters="isFiltersOpen = true"
        @clear-filters="onClearFilters"
        @export="onExportCsv"
        @refresh="loadData"
        @reset-columns="resetColumns"
        @apply-view="onApplyView"
        @save-view="onSaveView"
        @delete-view="savedViewsComposable.deleteView"
      />
    </div>

    <!-- Desktop View: DataTable (hidden on < md) -->
    <div class="hidden md:block">
      <DataTable
        :rows="rows"
        :columns="adaptedColumns"
        :fields="meta.fields"
        :resource-key="resourceKey"
        :resource-title="meta.title"
        :meta="meta"
        :hidden-columns="hiddenColumns"
        :column-order="columnOrder"
        :column-widths="columnWidths"
        :ordering="ordering"
        :selected-row-ids="selectedRowIds"
        :is-page-selected="isPageSelected"
        :is-page-partially-selected="isPagePartiallySelected"
        :density="density"
        :loading="loading"
        :is-fetching="isFetching"
        :error="error"
        :page-size="pageSize"
        :has-filters="hasActiveFilters"
        @sort="sortBy"
        @row-click="onRowClick"
        @row-open-new-tab="onRowOpenNewTab"
        @toggle-select="toggleRowSelection"
        @select-all="toggleSelectPage"
        @clear-filters="onClearFilters"
        @create="onCreateNew"
        @retry="loadData"
        @resize-column="onResizeColumn"
        @view="openDetail"
        @edit="openEdit"
        @duplicate="onDuplicate"
        @delete="onDeleteRow"
      />
    </div>

    <!-- Mobile View: Card List (< md) -->
    <div class="block md:hidden space-y-2.5">
      <!-- Loading skeleton -->
      <template v-if="loading && rows.length === 0">
        <div v-for="n in 5" :key="n" class="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 animate-pulse space-y-2">
          <div class="flex justify-between items-center">
            <div class="h-4 w-24 bg-slate-200 dark:bg-slate-800 rounded" />
            <div class="h-4 w-16 bg-slate-200 dark:bg-slate-800 rounded-full" />
          </div>
          <div class="h-3 w-40 bg-slate-200 dark:bg-slate-800 rounded" />
        </div>
      </template>

      <!-- Actual Cards -->
      <template v-else-if="rows.length > 0">
        <div
          v-for="row in rows"
          :key="row.id"
          class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs hover:border-brand-500/50 transition-colors active:bg-slate-50 dark:active:bg-slate-800/80 cursor-pointer"
          @click="onRowClick(row)"
        >
          <!-- Top Row: ID / Number and Status -->
          <div class="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800/60">
            <div class="flex items-center gap-2">
              <input
                type="checkbox"
                :checked="selectedRowIds.includes(row.id)"
                class="rounded border-slate-300 text-brand-600 focus:ring-brand-500 h-4 w-4"
                @click.stop
                @change="toggleRowSelection(row.id)"
              />
              <span class="font-mono text-xs font-bold text-slate-900 dark:text-slate-100">
                #{{ row.number || row.code || row.id }}
              </span>
            </div>
            <StatusPill
              v-if="row.status"
              :status="row.status"
              :label="row.status_label"
              size="sm"
            />
          </div>

          <!-- Key Fields Summary -->
          <div class="py-2.5 grid grid-cols-2 gap-2 text-xs">
            <div v-for="col in mobileKeyColumns" :key="col.name" class="space-y-0.5">
              <span class="text-[10px] font-medium text-slate-400 uppercase tracking-wider block">
                {{ col.label }}
              </span>
              <div class="truncate text-slate-800 dark:text-slate-200 font-medium">
                <CellDispatcher
                  :row="row"
                  :name="col.name"
                  :field="meta.fields[col.name]"
                  :resource-key="resourceKey"
                />
              </div>
            </div>
          </div>

          <!-- Bottom Footer: Timestamp and Chevron -->
          <div class="pt-2 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
            <span>{{ formatRelative(row.created_at || row.updated_at) }}</span>
            <span class="inline-flex items-center text-brand-600 dark:text-brand-400 font-medium gap-0.5">
              <span>View</span>
              <ChevronRight class="w-3.5 h-3.5" />
            </span>
          </div>
        </div>
      </template>

      <!-- Empty State -->
      <div v-if="!loading && rows.length === 0" class="p-8 text-center rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
        <EmptyState
          :title="hasActiveFilters ? 'No matching records' : `No ${meta.title.toLowerCase()} yet`"
          :action-label="hasActiveFilters ? 'Clear filters' : (meta.create ? 'Create first record' : undefined)"
          @action="hasActiveFilters ? onClearFilters() : onCreateNew()"
        />
      </div>
    </div>

    <!-- Pagination -->
    <DataTablePagination
      :page="page"
      :page-size="pageSize"
      :total="total"
      @update:page="onPageChange"
      @update:page-size="onPageSizeChange"
    />

    <!-- Selection Bulk Action Bar (Slides from bottom) -->
    <DataTableBulkBar
      :selected-count="selectedRowIds.length"
      :total-count="total"
      :is-all-matching="selectAllMatching"
      :allow-delete="meta.create !== false && !meta.readonly"
      @clear="clearSelection"
      @select-all-matching="onSelectAllMatching"
      @export-selected="onExportSelected"
      @delete-selected="onDeleteSelected"
    />

    <!-- Slide-over Filters Drawer -->
    <DataTableFilters
      :open="isFiltersOpen"
      :meta="meta"
      :filters="filterComposable.filters.value"
      :dates="filterComposable.dates.value"
      @update:open="isFiltersOpen = $event"
      @apply="onApplyFiltersDrawer"
      @reset="filterComposable.clearAll"
    />

    <!-- Slide-over Quick View Drawer -->
    <ResourceQuickView
      :open="isQuickViewOpen"
      :record="selectedRecord"
      :resource-key="resourceKey"
      :meta="meta"
      @update:open="isQuickViewOpen = $event"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, ChevronRight } from 'lucide-vue-next'
import api, { errText } from '../../api'
import { formatRelative } from '../../utils/format'
import { useToast } from '../../composables/useToast'
import { useConfirm } from '../../composables/useConfirm'
import { useFilters } from '../../composables/useFilters'
import { useTable } from '../../composables/useTable'
import { useSavedViews } from '../../composables/useSavedViews'
import { useCsvExport } from '../../composables/useCsvExport'
import { useUrlState } from '../../composables/useUrlState'

import Button from '../ui/Button.vue'
import StatusPill from '../ui/StatusPill.vue'
import EmptyState from '../feedback/EmptyState.vue'
import DataTable from '../data-table/DataTable.vue'
import DataTableToolbar from '../data-table/DataTableToolbar.vue'
import DataTableFilters from '../data-table/DataTableFilters.vue'
import DataTablePagination from '../data-table/DataTablePagination.vue'
import DataTableBulkBar from '../data-table/DataTableBulkBar.vue'
import CellDispatcher from '../data-table/cells/CellDispatcher.vue'
import ResourceQuickView from './ResourceQuickView.vue'

const props = defineProps({
  resourceKeyProp: String,
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const confirm = useConfirm()

// Active Resource Key
const resourceKey = computed(() => props.resourceKeyProp || route.params.key)

// Metadata
const meta = ref(null)

// Composables setup
const filterComposable = useFilters(meta)
const tableComposable = useTable(resourceKey, meta, filterComposable)
const savedViewsComposable = useSavedViews(resourceKey)
const csvExport = useCsvExport()

// Destructure table state
const {
  page,
  pageSize,
  ordering,
  search,
  status,
  density,
  rows,
  total,
  counts,
  loading,
  isFetching,
  error,
  lastUpdated,
  selectedRowIds,
  selectAllMatching,
  hiddenColumns,
  columnOrder,
  columnWidths,
  isPageSelected,
  isPagePartiallySelected,
  loadData,
  sortBy,
  setDensity,
  toggleRowSelection,
  toggleSelectPage,
  clearSelection,
} = tableComposable

// Modal / Drawer states
const isFiltersOpen = ref(false)
const isQuickViewOpen = ref(false)
const selectedRecord = ref(null)

// Two-way URL state sync
const urlState = useUrlState(
  {
    search: '',
    status: 'all',
    page: 1,
    page_size: 20,
    ordering: '',
  },
  { debounceMs: 150 }
)

// Sync URL state -> Table state
watch(
  urlState.state,
  (s) => {
    if (s.search !== undefined && s.search !== search.value) search.value = s.search
    if (s.status !== undefined && s.status !== status.value) status.value = s.status
    if (s.page !== undefined && Number(s.page) !== page.value) page.value = Number(s.page)
    if (s.page_size !== undefined && Number(s.page_size) !== pageSize.value) pageSize.value = Number(s.page_size)
    if (s.ordering !== undefined && s.ordering !== ordering.value) ordering.value = s.ordering

    // Synchronize filters from route.query
    if (meta.value?.filters) {
      for (const f of meta.value.filters) {
        if (route.query[f.name] !== undefined) {
          const val = route.query[f.name]
          filterComposable.filters.value[f.name] = isNaN(val) ? val : Number(val)
        }
      }
    }
  },
  { immediate: true }
)

// Sync Table state -> URL state
watch([search, status, page, pageSize, ordering, filterComposable.filters, filterComposable.dates], () => {
  const next = {
    search: search.value || undefined,
    status: status.value !== 'all' ? status.value : undefined,
    page: page.value > 1 ? page.value : undefined,
    page_size: pageSize.value !== 20 ? pageSize.value : undefined,
    ordering: ordering.value || undefined,
  }
  for (const [k, v] of Object.entries(filterComposable.filters.value)) {
    if (v !== undefined && v !== null && v !== '' && v !== 'all') {
      next[k] = v
    }
  }
  urlState.state.value = next
})

// Columns
const allColumns = computed(() => {
  if (!meta.value?.columns) return []
  return meta.value.columns.map((c) => ({
    name: c,
    label: meta.value.fields?.[c]?.label || c.replace(/_/g, ' ').replace(/^./, (s) => s.toUpperCase()),
  }))
})

const adaptedColumns = computed(() => {
  if (!meta.value?.columns) return []
  return meta.value.columns.map((colName) => {
    const field = meta.value.fields?.[colName]
    const isMoney = field?.money || ['sell_rate', 'buy_rate', 'rate', 'total', 'amount', 'cost', 'margin'].includes(colName)
    const isNumeric = ['int', 'float', 'decimal'].includes(field?.type) || colName.endsWith('_km') || colName.endsWith('_t')
    return {
      name: colName,
      label: field?.label || colName.replace(/_/g, ' ').replace(/^./, (s) => s.toUpperCase()),
      sortable: field?.type !== 'computed',
      align: isMoney || isNumeric ? 'right' : 'left',
    }
  })
})

const mobileKeyColumns = computed(() => {
  if (!meta.value?.columns) return []
  const ignored = new Set(['id', 'number', 'code', 'status', 'created_at', 'updated_at'])
  return meta.value.columns
    .filter((c) => !ignored.has(c))
    .slice(0, 4)
    .map((c) => ({
      name: c,
      label: meta.value.fields?.[c]?.label || c.replace(/_/g, ' '),
    }))
})

// Status tabs
const statusTabs = computed(() => {
  if (!meta.value?.status_choices?.length) return []
  return [{ value: 'all', label: 'All' }, ...meta.value.status_choices]
})

const singularTitle = computed(() => {
  const t = meta.value?.title || 'Record'
  return t.endsWith('s') ? t.slice(0, -1) : t
})

const hasActiveFilters = computed(() => {
  return filterComposable.activeCount.value > 0 || status.value !== 'all' || !!search.value
})

// Column Actions
function resetColumns() {
  hiddenColumns.value = []
  columnOrder.value = []
}

function onResizeColumn({ column, width }) {
  tableComposable.setColumnWidth(column, width)
}

// Handlers
function onSearchChange(val) {
  search.value = val
  page.value = 1
  loadData()
}

function onStatusChange(val) {
  status.value = val
  page.value = 1
  loadData()
}

function onPageChange(newPage) {
  page.value = newPage
  loadData()
}

function onPageSizeChange(newSize) {
  pageSize.value = newSize
  page.value = 1
  loadData()
}

function onClearFilters() {
  filterComposable.clearAll()
  search.value = ''
  status.value = 'all'
  page.value = 1
  loadData()
}

function onApplyFiltersDrawer({ filters: nextFilters, dates: nextDates }) {
  filterComposable.filters.value = nextFilters
  filterComposable.dates.value = nextDates
  page.value = 1
  loadData()
}

function onExportCsv() {
  csvExport.exportCsv(resourceKey.value, tableComposable.buildParams(true), meta.value)
}

function onSelectAllMatching() {
  selectAllMatching.value = true
  toast.info(`Selected all ${total.value} matching records`)
}

function onExportSelected() {
  const ids = selectAllMatching.value ? [] : selectedRowIds.value
  toast.success(`Exporting ${ids.length ? ids.length : total.value} selected records…`)
  csvExport.exportCsv(resourceKey.value, tableComposable.buildParams(true), meta.value)
}

async function onDeleteSelected() {
  const count = selectAllMatching.value ? total.value : selectedRowIds.value.length
  const confirmed = await confirm.danger({
    title: `Delete ${count} records?`,
    message: `Are you sure you want to permanently delete these ${count} records? This action cannot be undone.`,
    confirmText: 'Delete selected',
  })
  if (confirmed) {
    toast.error('Bulk deletion is disabled by server policy')
  }
}

// Row navigation
function onRowClick(row) {
  selectedRecord.value = row
  isQuickViewOpen.value = true
}

function onRowOpenNewTab(row) {
  const url = resourceKey.value === 'orders' ? `/orders/${row.id}` : `/r/${resourceKey.value}/${row.id}`
  window.open(url, '_blank')
}

function openDetail(row) {
  const url = resourceKey.value === 'orders' ? `/orders/${row.id}` : `/r/${resourceKey.value}/${row.id}`
  router.push(url)
}

function openEdit(row) {
  router.push(`/r/${resourceKey.value}/${row.id}/edit`)
}

function onDuplicate(row) {
  toast.info(`Duplicating #${row.number || row.id}…`)
  router.push({
    path: `/r/${resourceKey.value}/new`,
    query: { duplicate_from: row.id },
  })
}

async function onDeleteRow(row) {
  try {
    await api.delete(`${resourceKey.value}/${row.id}/`)
    toast.success('Record deleted')
    loadData()
  } catch (e) {
    toast.error(`Delete failed: ${errText(e)}`)
  }
}

function onCreateNew() {
  router.push(`/r/${resourceKey.value}/new`)
}

// Saved Views
function onApplyView(view) {
  savedViewsComposable.activeViewId.value = view.id
  if (view.state.filters) filterComposable.filters.value = { ...view.state.filters }
  if (view.state.dates) filterComposable.dates.value = { ...view.state.dates }
  if (view.state.search !== undefined) search.value = view.state.search
  if (view.state.status) status.value = view.state.status
  if (view.state.ordering) ordering.value = view.state.ordering
  if (view.state.density) setDensity(view.state.density)
  if (view.state.hiddenColumns) hiddenColumns.value = [...view.state.hiddenColumns]
  if (view.state.columnOrder) columnOrder.value = [...view.state.columnOrder]
  page.value = 1
  loadData()
  toast.success(`Switched to view "${view.name}"`)
}

function onSaveView(name) {
  savedViewsComposable.saveView(name, {
    filters: filterComposable.filters.value,
    dates: filterComposable.dates.value,
    search: search.value,
    status: status.value,
    ordering: ordering.value,
    density: density.value,
    hiddenColumns: hiddenColumns.value,
    columnOrder: columnOrder.value,
  })
  toast.success(`Saved view "${name}"`)
}

// Initialize on mount
async function initMeta() {
  loading.value = true
  try {
    const res = await api.get(`meta/${resourceKey.value}/`)
    meta.value = res.data

    // Hydrate filters from route.query
    for (const [k, v] of Object.entries(route.query)) {
      if (meta.value.filters?.some((f) => f.name === k)) {
        filterComposable.filters.value[k] = isNaN(v) ? v : Number(v)
      }
    }

    loadData()
  } catch (e) {
    error.value = errText(e)
    loading.value = false
  }
}

watch(resourceKey, () => {
  meta.value = null
  initMeta()
})

onMounted(() => {
  initMeta()
})
</script>
