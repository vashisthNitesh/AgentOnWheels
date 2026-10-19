import { ref, computed, watch, onUnmounted } from 'vue'
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
  const page = ref(1)
  const pageSize = ref(20)
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

  // Storage key helpers
  const key = computed(() => resourceKeyRef.value || resourceKeyRef)
  const colsStorageKey = computed(() => `aow_cols_${key.value}`)
  const widthsStorageKey = computed(() => `aow_widths_${key.value}`)
  const densityStorageKey = computed(() => `aow_density_${key.value}`)

  // Initialize storage preferences
  function loadPreferences() {
    try {
      const storedCols = localStorage.getItem(colsStorageKey.value)
      if (storedCols) hiddenColumns.value = JSON.parse(storedCols)

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
    columnWidths.value = { ...columnWidths.value, [colName]: Math.max(60, width) }
    try {
      localStorage.setItem(widthsStorageKey.value, JSON.stringify(columnWidths.value))
    } catch {}
  }

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

  // Request cancellation & sequencing
  let abortController = null
  let requestSeq = 0

  async function loadData() {
    const currentSeq = ++requestSeq

    // Cancel any ongoing fetch
    if (abortController) {
      abortController.abort()
    }
    abortController = new AbortController()

    // Determine loading indicators
    if (rows.value.length === 0) {
      loading.value = true
    } else {
      isFetching.value = true
    }
    error.value = ''

    try {
      const currentKey = key.value
      const meta = metaRef.value

      const listPromise = api.get(`${currentKey}/`, {
        params: buildParams(true),
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

  // Cleanup on unmount
  onUnmounted(() => {
    if (abortController) {
      abortController.abort()
    }
  })

  // Watch resource key changes
  watch(
    key,
    () => {
      loadPreferences()
      page.value = 1
      clearSelection()
      loadData()
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
    setDensity,
    toggleRowSelection,
    toggleSelectPage,
    clearSelection,
  }
}
