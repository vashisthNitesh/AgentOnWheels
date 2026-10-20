<template>
  <!--
    Full-height list layout: header + one card that fills the remaining
    viewport. Only the table body scrolls (both axes); the page never does.
    On small screens the card list falls back to natural page scrolling.
  -->
  <div class="mx-auto flex w-full max-w-[1600px] flex-1 flex-col gap-3 md:h-[calc(100dvh-3.5rem-2rem)] md:min-h-[480px] md:flex-none lg:h-[calc(100dvh-3.5rem-3rem)]">
    <!-- Header -->
    <header class="flex shrink-0 flex-wrap items-center justify-between gap-3">
      <div class="flex min-w-0 items-center gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-border-default bg-surface text-primary-600 shadow-xs dark:text-primary-400">
          <component :is="moduleIcon" class="h-5 w-5" />
        </div>
        <div class="min-w-0">
          <div class="flex items-center gap-2">
            <h1 class="truncate text-lg font-semibold tracking-tight text-primary sm:text-xl">
              <template v-if="meta">{{ meta.title }}</template>
              <span v-else class="inline-block h-6 w-40 animate-pulse rounded bg-muted align-middle" />
            </h1>
            <span
              v-if="meta?.group"
              class="hidden rounded-md bg-muted px-1.5 py-0.5 text-[11px] font-medium text-muted sm:inline"
            >
              {{ meta.group }}
            </span>
          </div>
          <p class="text-xs text-muted">
            <template v-if="!meta || (loading && !rows.length)">Loading…</template>
            <template v-else>
              {{ total.toLocaleString() }} {{ total === 1 ? 'record' : 'records' }}
              <template v-if="hasActiveFilters"> matching filters</template>
              <span v-if="meta.key === 'trips'"> · counted per leg</span>
            </template>
          </p>
        </div>
      </div>

      <Button v-if="meta?.create" variant="primary" size="md" @click="onCreateNew">
        <Plus class="h-4 w-4" />
        <span>New {{ singularTitle }}</span>
      </Button>
    </header>

    <!-- Card: toolbar · table · footer -->
    <section
      class="relative flex min-h-[420px] flex-1 flex-col overflow-hidden rounded-xl border border-border-default bg-surface shadow-sm md:min-h-[320px]"
    >
      <template v-if="!meta && !error">
        <div class="space-y-3 p-4">
          <div class="h-9 w-full animate-pulse rounded-lg bg-muted" />
          <div v-for="n in 8" :key="n" class="h-10 w-full animate-pulse rounded-md bg-muted/60" />
        </div>
      </template>

      <div v-else-if="!meta && error" class="flex flex-1 items-center justify-center p-8">
        <EmptyState variant="error" :description="error" action-text="Retry" @action="initMeta" />
      </div>

      <template v-else>
        <DataTableToolbar
          class="shrink-0 border-b border-border-default"
          :search="search"
          :status="status"
          :status-tabs="statusTabs"
          :counts="counts"
          :active-filters-count="filterComposable.activeCount.value"
          :filter-chips="filterComposable.chips.value"
          :all-columns="allColumns"
          :hidden-columns="hiddenColumns"
          :column-order="columnOrder"
          :has-custom-widths="Object.keys(columnWidths).length > 0"
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
          @filters-changed="onFiltersChanged"
          @export="onExportCsv"
          @refresh="loadData"
          @reset-columns="resetColumns"
          @apply-view="onApplyView"
          @save-view="onSaveView"
          @delete-view="savedViewsComposable.deleteView"
        />

        <!-- Desktop table -->
        <DataTable
          class="hidden md:flex"
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
          @sort="onSort"
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

        <!-- Mobile cards -->
        <div class="flex-1 space-y-2 p-2.5 md:hidden">
          <template v-if="loading && !rows.length">
            <div v-for="n in 5" :key="n" class="space-y-2 rounded-lg border border-border-default p-3.5">
              <div class="flex items-center justify-between">
                <div class="h-4 w-24 animate-pulse rounded bg-muted" />
                <div class="h-5 w-16 animate-pulse rounded-full bg-muted" />
              </div>
              <div class="h-3 w-40 animate-pulse rounded bg-muted" />
            </div>
          </template>

          <template v-else-if="rows.length">
            <article
              v-for="row in rows"
              :key="row.id"
              :class="[
                'cursor-pointer rounded-lg border p-3.5 transition-colors active:bg-subtle',
                selectedRowIds.includes(row.id)
                  ? 'border-primary-300 bg-primary-50/60 dark:border-primary-800 dark:bg-primary-950/60'
                  : 'border-border-default bg-surface'
              ]"
              @click="onRowClick(row)"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="flex min-w-0 items-center gap-2.5">
                  <Checkbox
                    :model-value="selectedRowIds.includes(row.id)"
                    :aria-label="`Select ${row.number || row.code || row.id}`"
                    @update:model-value="toggleRowSelection(row.id)"
                  />
                  <span class="truncate font-mono text-[13px] font-semibold text-primary">
                    {{ row.number || row.code || row.name || `#${row.id}` }}
                  </span>
                </div>
                <StatusPill
                  v-if="row[meta.status || 'status']"
                  :status="row[meta.status || 'status']"
                  :label="row[`${meta.status || 'status'}_label`] || row.status_label"
                  size="sm"
                />
              </div>

              <dl class="mt-3 grid grid-cols-2 gap-x-3 gap-y-2.5 text-xs">
                <div v-for="col in mobileKeyColumns" :key="col.name" class="min-w-0">
                  <dt class="text-[11px] text-muted">{{ col.label }}</dt>
                  <dd class="mt-0.5 truncate font-medium text-primary">
                    <CellDispatcher :row="row" :name="col.name" :field="meta.fields[col.name]" :resource-key="resourceKey" />
                  </dd>
                </div>
              </dl>

              <div class="mt-3 flex items-center justify-between border-t border-border-default pt-2.5 text-[11px] text-muted">
                <span>{{ formatRelative(row.updated_at || row.created_at) }}</span>
                <span class="inline-flex items-center gap-0.5 font-medium text-primary-600 dark:text-primary-400">
                  Open <ChevronRight class="h-3.5 w-3.5" />
                </span>
              </div>
            </article>
          </template>

          <EmptyState
            v-else-if="!error"
            :variant="hasActiveFilters ? 'no-results' : 'no-data'"
            :default-actions="false"
            :title="hasActiveFilters ? 'No matching records' : `No ${meta.title.toLowerCase()} yet`"
            :action-text="hasActiveFilters ? 'Clear filters' : (meta.create ? `New ${singularTitle.toLowerCase()}` : '')"
            @action="hasActiveFilters ? onClearFilters() : onCreateNew()"
          />
          <EmptyState v-else variant="error" :description="error" action-text="Retry" @action="loadData" />
        </div>

        <!-- Footer -->
        <DataTablePagination
          class="shrink-0 border-t border-border-default bg-surface"
          :page="page"
          :page-size="pageSize"
          :total="total"
          @update:page="onPageChange"
          @update:page-size="onPageSizeChange"
        />

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
      </template>
    </section>

    <DataTableFilters
      v-if="meta"
      :open="isFiltersOpen"
      :meta="meta"
      :filters="filterComposable.filters.value"
      :dates="filterComposable.dates.value"
      @update:open="isFiltersOpen = $event"
      @apply="onApplyFiltersDrawer"
      @reset="filterComposable.clearAll"
    />

    <ResourceQuickView
      v-if="meta"
      :open="isQuickViewOpen"
      :record="selectedRecord"
      :resource-key="resourceKey"
      :meta="meta"
      @update:open="isQuickViewOpen = $event"
      @edit="openEdit"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, ChevronRight } from 'lucide-vue-next'
import { getModuleIcon } from '../../layouts/moduleIcons'
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
import Checkbox from '../ui/Checkbox.vue'
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
  setColumnWidth,
  resetColumnWidths,
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
    // Only honour page_size when it is explicitly in the URL; otherwise keep the
    // user's saved rows-per-page preference.
    if (route.query.page_size && Number(route.query.page_size) !== pageSize.value) pageSize.value = Number(route.query.page_size)
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
    page_size: undefined, // rows-per-page is a stored preference, not URL state
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
      width: defaultWidth(colName, field, isMoney, isNumeric),
    }
  })
})

function defaultWidth(name, field, isMoney, isNumeric) {
  if (['id', 'number', 'code', 'reference'].includes(name) || name.endsWith('_ref')) return 180
  if (name === 'status' || name.endsWith('_status')) return 200
  if (isMoney) return 140
  if (isNumeric) return 120
  if (field?.type === 'bool') return 100
  if (field?.type === 'date') return 130
  if (field?.type === 'datetime' || name.endsWith('_at')) return 170
  if (field?.type === 'fk' || ['customer', 'vendor', 'driver', 'vehicle'].includes(name)) return 210
  if (name.includes('name') || name.includes('title') || name.includes('description')) return 220
  if (name.includes('email') || name.includes('address')) return 230
  return 160
}

const moduleIcon = computed(() => getModuleIcon(resourceKey.value))

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
  resetColumnWidths()
  toast.success('Column layout reset')
}

function onResizeColumn({ column, width }) {
  setColumnWidth(column, width)
}

function onSort(col) {
  sortBy(col)
  page.value = 1
  loadData()
}

function onFiltersChanged() {
  page.value = 1
  loadData()
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
function detailPath(row) {
  return resourceKey.value === 'orders' ? `/orders/${row.id}` : `/r/${resourceKey.value}/${row.id}`
}

function onRowClick(row) {
  selectedRecord.value = row
  isQuickViewOpen.value = true
}

function onRowOpenNewTab(row) {
  window.open(router.resolve(detailPath(row)).href, '_blank', 'noopener')
}

function openDetail(row) {
  router.push(detailPath(row))
}

function openEdit(row) {
  isQuickViewOpen.value = false
  router.push(`/r/${resourceKey.value}/${row.id}/edit`)
}

function onDuplicate(row) {
  router.push({
    path: `/r/${resourceKey.value}/new`,
    query: { duplicate_from: row.id },
  })
}

async function onDeleteRow(row) {
  try {
    await api.delete(`${resourceKey.value}/${row.id}/`)
    toast.success('Record deleted')
    selectedRowIds.value = selectedRowIds.value.filter((id) => id !== row.id)
    // Step back a page if we just removed the last row on it.
    if (rows.value.length === 1 && page.value > 1) page.value -= 1
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
  error.value = ''
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
