import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

/**
 * useUrlState
 * Synchronizes reactive state with route.query using router.replace.
 * Avoids history stack pollution during filtering, searching, or pagination.
 */
export function useUrlState(initialState = {}, { debounceMs = 0 } = {}) {
  const route = useRoute()
  const router = useRouter()

  const state = ref({ ...initialState })
  let isInternalUpdate = false
  let debounceTimer = null

  // Hydrate state from route query
  function hydrateFromQuery() {
    if (isInternalUpdate) return
    const query = route.query
    const next = { ...initialState }

    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null || value === '') continue

      // Boolean parsing
      if (value === 'true') next[key] = true
      else if (value === 'false') next[key] = false
      // Number parsing
      else if (!isNaN(value) && !isNaN(parseFloat(value)) && typeof value === 'string' && !value.includes('-')) {
        next[key] = Number(value)
      } else {
        next[key] = value
      }
    }
    state.value = next
  }

  // Push state changes to route query
  function syncToQuery() {
    isInternalUpdate = true
    const currentQuery = { ...route.query }
    const newQuery = {}

    for (const [k, v] of Object.entries(state.value)) {
      if (v === undefined || v === null || v === '' || v === 'all') continue
      // Don't clutter URL if it's default initial state
      if (initialState[k] !== undefined && initialState[k] === v) continue
      newQuery[k] = String(v)
    }

    // Preserve any unrelated route queries
    for (const [k, v] of Object.entries(currentQuery)) {
      if (!(k in initialState) && !(k in state.value)) {
        newQuery[k] = v
      }
    }

    // Compare if query changed
    const currentKeys = Object.keys(currentQuery).sort()
    const newKeys = Object.keys(newQuery).sort()
    const hasChanged =
      currentKeys.length !== newKeys.length ||
      currentKeys.some((k) => String(currentQuery[k]) !== String(newQuery[k]))

    if (hasChanged) {
      router
        .replace({ query: newQuery })
        .catch(() => {})
        .finally(() => {
          setTimeout(() => {
            isInternalUpdate = false
          }, 50)
        })
    } else {
      isInternalUpdate = false
    }
  }

  // Watch state changes
  watch(
    state,
    () => {
      if (debounceMs > 0) {
        clearTimeout(debounceTimer)
        debounceTimer = setTimeout(syncToQuery, debounceMs)
      } else {
        syncToQuery()
      }
    },
    { deep: true }
  )

  // Watch route query changes (e.g. browser back/forward)
  watch(
    () => route.query,
    () => {
      hydrateFromQuery()
    },
    { immediate: true, deep: true }
  )

  return {
    state,
    syncToQuery,
    hydrateFromQuery,
  }
}
