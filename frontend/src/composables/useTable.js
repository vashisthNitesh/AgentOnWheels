import { ref, computed, watch, onUnmounted, unref } from 'vue'
import api, { errText } from '../api'

/**
 * useTable
 * Core table state management:
 * - Pagination, sorting, search, status tabs
 * - Row selection & "select all matching"
 * - Column visibility, ordering, widths, density
 * - Safe data fetching with AbortController, request sequencing, and loading states
 */
export function useTable(resourceKeyRef, metaRef, filterComposable) {
  // Core state
  const PAGE_SIZE_KEY = 'aow_page_size'
  const page = ref(1)
  const pageSize = ref(readPageSize())
  const ordering = ref('')
  const search = ref('')
  const status = ref('all')
  const density = ref('normal') // 'compact' | 'normal' | 'relaxed'

  // Data & loading states
  const rows = ref([])
  const total = ref(0)
  const counts = ref(null)
  const loading = ref(true) // Initial load
  const isFetching = ref(false) // Refetching in background
  const error = ref('')
  const lastUpdated = ref(new Date())

  // Selection
  const selectedRowIds = ref([])
  const selectAllMatching = ref(false)

  // Column preferences
  const hiddenColumns = ref([])
  const columnOrder = ref([])
  const columnWidths = ref({})

  function readPageSize() {
    try {
      const v = Number(localStorage.getItem(PAGE_SIZE_KEY))
      if ([10, 20, 50, 100].includes(v)) return v
    } catch {}
    return 20
  }

  // Storage key helpers
  const key = computed(() => unref(resourceKeyRef))
  const colsStorageKey = computed(() => `aow_cols_${key.value}`)
  const orderStorageKey = computed(() => `aow_order_${key.value}`)
  const widthsStorageKey = computed(() => `aow_widths_${key.value}`)
  const densityStorageKey = computed(() => `aow_density_${key.value}`)

  // Initialize storage preferences
  function loadPreferences() {
    try {
      const storedCols = localStorage.getItem(colsStorageKey.value)
      if (storedCols) hiddenColumns.value = JSON.parse(storedCols)

      const storedOrder = localStorage.getItem(orderStorageKey.value)
      if (storedOrder) columnOrder.value = JSON.parse(storedOrder)

      const storedWidths = localStorage.getItem(widthsStorageKey.value)
      if (storedWidths) columnWidths.value = JSON.parse(storedWidths)

      const storedDensity = localStorage.getItem(densityStorageKey.value)
      if (storedDensity) density.value = storedDensity
    } catch {}
  }

  function toggleColumn(colName) {
    if (hiddenColumns.value.includes(colName)) {
      hiddenColumns.value = hiddenColumns.value.filter((c) => c !== colName)
    } else {
      hiddenColumns.value = [...hiddenColumns.value, colName]
    }
    try {
      localStorage.setItem(colsStorageKey.value, JSON.stringify(hiddenColumns.value))
    } catch {}
  }

  function setColumnWidth(colName, width) {
    const next = { ...columnWidths.value }
    if (width === null || width === undefined) delete next[colName]
    else next[colName] = Math.max(60, Math.round(width))
    columnWidths.value = next
    try {
      localStorage.setItem(widthsStorageKey.value, JSON.stringify(columnWidths.value))
    } catch {}
  }

  function resetColumnWidths() {
    columnWidths.value = {}
    try {
      localStorage.removeItem(widthsStorageKey.value)
    } catch {}
  }

  // Persist column visibility / order whenever they change (from any source).
  watch(hiddenColumns, (v) => {
    try {
      localStorage.setItem(colsStorageKey.value, JSON.stringify(v))
    } catch {}
  })
  watch(columnOrder, (v) => {
    try {
      if (v?.length) localStorage.setItem(orderStorageKey.value, JSON.stringify(v))
      else localStorage.removeItem(orderStorageKey.value)
    } catch {}
  })
  // Rows-per-page is a global preference shared by every list.
  watch(pageSize, (v) => {
    try {
      localStorage.setItem(PAGE_SIZE_KEY, String(v))
    } catch {}
  })

  function setDensity(d) {
    density.value = d
    try {
      localStorage.setItem(densityStorageKey.value, d)
    } catch {}
  }

  // Selection helpers
  function toggleRowSelection(rowId) {
    if (selectedRowIds.value.includes(rowId)) {
      selectedRowIds.value = selectedRowIds.value.filter((id) => id !== rowId)
      selectAllMatching.value = false
    } else {
      selectedRowIds.value = [...selectedRowIds.value, rowId]
    }
  }

  function toggleSelectPage(checked) {
    if (checked) {
      const pageIds = rows.value.map((r) => r.id)
      selectedRowIds.value = Array.from(new Set([...selectedRowIds.value, ...pageIds]))
    } else {
      const pageIdSet = new Set(rows.value.map((r) => r.id))
      selectedRowIds.value = selectedRowIds.value.filter((id) => !pageIdSet.has(id))
      selectAllMatching.value = false
    }
  }

  function clearSelection() {
    selectedRowIds.value = []
    selectAllMatching.value = false
  }

  const isPageSelected = computed(() => {
    if (rows.value.length === 0) return false
    return rows.value.every((r) => selectedRowIds.value.includes(r.id))
  })

  const isPagePartiallySelected = computed(() => {
    if (rows.value.length === 0) return false
    const some = rows.value.some((r) => selectedRowIds.value.includes(r.id))
    return some && !isPageSelected.value
  })

  // Sorting
  function sortBy(colName) {
    if (metaRef.value?.fields?.[colName]?.type === 'computed') return
    if (ordering.value === colName) {
      ordering.value = `-${colName}`
    } else if (ordering.value === `-${colName}`) {
      ordering.value = ''
    } else {
      ordering.value = colName
    }
  }

  // Params builder
  function buildParams(withStatus = true) {
    const filterParams = filterComposable ? filterComposable.toApiParams({ includeStatus: withStatus, statusValue: status.value }) : {}
    const p = {
      page: page.value,
      page_size: pageSize.value,
      ...filterParams,
    }
    if (search.value) p.search = search.value
    if (ordering.value) p.ordering = ordering.value
    return p
  }

  // Global in-memory table cache for instant tab navigation (stale-while-revalidate)
  const tableCache = new Map()

  // Request cancellation & sequencing
  let abortController = null
  let requestSeq = 0

  async function loadData(forceFresh = false) {
    const currentSeq = ++requestSeq

    // Cancel any ongoing fetch
    if (abortController) {
      abortController.abort()
    }
    abortController = new AbortController()

    const currentKey = key.value
    const p = buildParams(true)
    const ck = `${currentKey}:${JSON.stringify(p)}`

    // Fast cache check: if cached, render immediately without showing a blank loading skeleton
    const cached = !forceFresh ? tableCache.get(ck) : null
    if (cached) {
      rows.value = cached.rows
      total.value = cached.total
      if (cached.counts) counts.value = cached.counts
      loading.value = false
      isFetching.value = true
    } else if (rows.value.length === 0) {
      loading.value = true
    } else {
      isFetching.value = true
    }
    error.value = ''

    try {
      const meta = metaRef.value

      const listPromise = api.get(`${currentKey}/`, {
        params: p,
        signal: abortController.signal,
      })

      const countsPromise =
        meta?.status
          ? api.get(`${currentKey}/counts/`, {
              params: buildParams(false),
              signal: abortController.signal,
            })
          : Promise.resolve(null)

      const [listRes, countsRes] = await Promise.all([listPromise, countsPromise])

      if (currentSeq !== requestSeq) return // Stale request

      rows.value = listRes.data.results || []
      total.value = listRes.data.count || 0
      counts.value = countsRes?.data || null
      lastUpdated.value = new Date()

      // Save to cache
      tableCache.set(ck, {
        rows: rows.value,
        total: total.value,
        counts: counts.value,
        time: Date.now(),
      })
    } catch (e) {
      if (e?.name === 'CanceledError' || e?.code === 'ERR_CANCELED') return
      if (currentSeq === requestSeq) {
        error.value = errText(e)
      }
    } finally {
      if (currentSeq === requestSeq) {
        loading.value = false
        isFetching.value = false
      }
    }
  }

  // Invalidate cache for a specific resource or all
  function invalidateCache(targetKey) {
    if (!targetKey) {
      tableCache.clear()
      return
    }
    for (const k of tableCache.keys()) {
      if (k.startsWith(`${targetKey}:`)) {
        tableCache.delete(k)
      }
    }
  }

  // Cleanup on unmount
  onUnmounted(() => {
    if (abortController) {
      abortController.abort()
    }
  })

  // Preferences load immediately; data is loaded by the page once metadata
  // is available (avoids a duplicate request without status counts).
  watch(
    key,
    (next, prev) => {
      loadPreferences()
      if (prev !== undefined) {
        page.value = 1
        clearSelection()
        loadData()
      }
    },
    { immediate: true }
  )

  return {
    // State
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

    // Computed
    isPageSelected,
    isPagePartiallySelected,

    // Actions
    loadData,
    buildParams,
    sortBy,
    toggleColumn,
    setColumnWidth,
    resetColumnWidths,
    setDensity,
    toggleRowSelection,
    toggleSelectPage,
    clearSelection,
    invalidateCache,
  }
}
