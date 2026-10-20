import { ref, computed } from 'vue'
import { formatDate } from '../utils/format'

/**
 * useFilters
 * Manages filter state, serialization to API query params, and filter chips.
 */
export function useFilters(metaRef, initialFilters = {}) {
  const filters = ref({ ...initialFilters })
  const dates = ref({})
  const refLabels = ref({}) // Cache for resolved FK labels: { [field_name]: { [id]: label } }

  // Set FK label cache
  function setRefLabel(field, id, label) {
    if (!refLabels.value[field]) refLabels.value[field] = {}
    refLabels.value[field][id] = label
  }

  // Count active filters
  const activeCount = computed(() => {
    let count = 0
    for (const [k, v] of Object.entries(filters.value)) {
      if (v !== undefined && v !== null && v !== '' && v !== 'all') {
        if (Array.isArray(v)) {
          if (v.length > 0) count++
        } else {
          count++
        }
      }
    }
    // A from/to pair is one date filter, not two.
    const ranges = new Set()
    for (const [k, v] of Object.entries(dates.value)) {
      if (v) ranges.add(k.replace(/_(from|to)$/, ''))
    }
    return count + ranges.size
  })

  // Convert to API query params
  function toApiParams(options = {}) {
    const { includeStatus = true, statusValue = 'all' } = options
    const p = {}
    const meta = metaRef.value
    if (!meta) return p

    for (const [k, v] of Object.entries(filters.value)) {
      if (v === undefined || v === null || v === '' || v === 'all') continue
      if (Array.isArray(v)) {
        if (v.length > 0) p[k] = v.join(',')
      } else {
        p[k] = v
      }
    }

    if (meta.dates && Array.isArray(meta.dates)) {
      for (const d of meta.dates) {
        const field = meta.fields?.[d.name]
        const dt = field?.type === 'datetime' ? '__date' : ''
        const fromVal = dates.value[`${d.name}_from`]
        const toVal = dates.value[`${d.name}_to`]
        if (fromVal) p[`${d.name}${dt}__gte`] = fromVal
        if (toVal) p[`${d.name}${dt}__lte`] = toVal
      }
    }

    if (includeStatus && meta.status && statusValue && statusValue !== 'all') {
      p[meta.status] = statusValue
    }

    return p
  }

  // Active filter chips
  const chips = computed(() => {
    const meta = metaRef.value
    if (!meta) return []
    const list = []

    // Field filters
    for (const [k, v] of Object.entries(filters.value)) {
      if (v === undefined || v === null || v === '' || v === 'all') continue
      const filterDef = meta.filters?.find((f) => f.name === k)
      const fieldDef = meta.fields?.[k]
      const label = filterDef?.label || fieldDef?.label || k.replace(/_/g, ' ')

      let displayValue = String(v)
      if (filterDef?.choices) {
        const match = filterDef.choices.find((c) => String(c.value) === String(v))
        if (match) displayValue = match.label
      } else if (filterDef?.type === 'bool') {
        displayValue = v === true || v === 'true' ? 'Yes' : 'No'
      } else if (filterDef?.type === 'fk' && refLabels.value[k]?.[v]) {
        displayValue = refLabels.value[k][v]
      }

      list.push({
        id: `filter_${k}`,
        key: k,
        label,
        value: v,
        displayValue,
        onRemove: () => {
          delete filters.value[k]
        },
      })
    }

    // Date filters
    if (meta.dates) {
      for (const d of meta.dates) {
        const fromVal = dates.value[`${d.name}_from`]
        const toVal = dates.value[`${d.name}_to`]
        if (fromVal || toVal) {
          let displayValue = ''
          if (fromVal && toVal) {
            displayValue = `${formatDate(fromVal)} – ${formatDate(toVal)}`
          } else if (fromVal) {
            displayValue = `From ${formatDate(fromVal)}`
          } else {
            displayValue = `Until ${formatDate(toVal)}`
          }

          list.push({
            id: `date_${d.name}`,
            key: d.name,
            label: d.label,
            displayValue,
            onRemove: () => {
              delete dates.value[`${d.name}_from`]
              delete dates.value[`${d.name}_to`]
            },
          })
        }
      }
    }

    return list
  })

  // Clear single filter
  function clearFilter(key) {
    if (key in filters.value) {
      delete filters.value[key]
    }
    if (`${key}_from` in dates.value || `${key}_to` in dates.value) {
      delete dates.value[`${key}_from`]
      delete dates.value[`${key}_to`]
    }
  }

  // Clear all filters
  function clearAll() {
    filters.value = {}
    dates.value = {}
  }

  return {
    filters,
    dates,
    activeCount,
    chips,
    toApiParams,
    clearFilter,
    clearAll,
    setRefLabel,
  }
}
