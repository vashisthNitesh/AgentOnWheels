import { ref, computed } from 'vue'

/**
 * useSavedViews
 * Manages custom user-saved views in localStorage per resource key.
 */
export function useSavedViews(resourceKey) {
  const storageKey = computed(() => `aow_saved_views_${resourceKey.value || resourceKey}`)
  const views = ref([])
  const activeViewId = ref(null)

  function loadViews() {
    try {
      const raw = localStorage.getItem(storageKey.value)
      if (raw) {
        views.value = JSON.parse(raw)
      } else {
        views.value = []
      }
    } catch {
      views.value = []
    }
  }

  function persist() {
    try {
      localStorage.setItem(storageKey.value, JSON.stringify(views.value))
    } catch (e) {
      console.warn('Failed to save views to localStorage', e)
    }
  }

  function saveView(name, state, isDefault = false) {
    const id = `view_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`
    if (isDefault) {
      views.value.forEach((v) => (v.isDefault = false))
    }
    const newView = {
      id,
      name,
      isDefault,
      createdAt: new Date().toISOString(),
      state: JSON.parse(JSON.stringify(state)),
    }
    views.value.push(newView)
    persist()
    activeViewId.value = id
    return newView
  }

  function updateView(id, state) {
    const idx = views.value.findIndex((v) => v.id === id)
    if (idx !== -1) {
      views.value[idx].state = JSON.parse(JSON.stringify(state))
      persist()
    }
  }

  function renameView(id, newName) {
    const view = views.value.find((v) => v.id === id)
    if (view) {
      view.name = newName
      persist()
    }
  }

  function deleteView(id) {
    views.value = views.value.filter((v) => v.id !== id)
    if (activeViewId.value === id) {
      activeViewId.value = null
    }
    persist()
  }

  function setDefaultView(id) {
    views.value.forEach((v) => {
      v.isDefault = v.id === id
    })
    persist()
  }

  const activeView = computed(() => views.value.find((v) => v.id === activeViewId.value) || null)
  const defaultView = computed(() => views.value.find((v) => v.isDefault) || null)

  function isModified(currentState) {
    if (!activeView.value) return false
    try {
      const a = JSON.stringify(activeView.value.state)
      const b = JSON.stringify(currentState)
      return a !== b
    } catch {
      return false
    }
  }

  // Initial load
  loadViews()

  return {
    views,
    activeViewId,
    activeView,
    defaultView,
    loadViews,
    saveView,
    updateView,
    renameView,
    deleteView,
    setDefaultView,
    isModified,
  }
}
