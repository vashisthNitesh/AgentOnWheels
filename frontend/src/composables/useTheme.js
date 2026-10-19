import { ref, computed, onMounted } from 'vue'

const THEME_KEY = 'aow-theme'
const currentTheme = ref('system')
const systemIsDark = ref(false)

function getMediaMatcher() {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)')
  }
  return null
}

function updateSystemState() {
  const matcher = getMediaMatcher()
  systemIsDark.value = matcher ? matcher.matches : false
}

function applyHtmlClass() {
  if (typeof document === 'undefined') return
  const isDark = currentTheme.value === 'dark' || (currentTheme.value === 'system' && systemIsDark.value)
  const root = document.documentElement
  if (isDark) {
    root.classList.add('dark')
    root.style.colorScheme = 'dark'
  } else {
    root.classList.remove('dark')
    root.style.colorScheme = 'light'
  }
}

let initialized = false

export function useTheme() {
  if (!initialized && typeof window !== 'undefined') {
    initialized = true
    const saved = localStorage.getItem(THEME_KEY)
    if (saved === 'light' || saved === 'dark' || saved === 'system') {
      currentTheme.value = saved
    } else {
      currentTheme.value = 'system'
    }

    updateSystemState()
    applyHtmlClass()

    const matcher = getMediaMatcher()
    if (matcher) {
      matcher.addEventListener('change', (e) => {
        systemIsDark.value = e.matches
        if (currentTheme.value === 'system') {
          applyHtmlClass()
        }
      })
    }
  }

  function setTheme(theme) {
    if (theme !== 'light' && theme !== 'dark' && theme !== 'system') return
    currentTheme.value = theme
    localStorage.setItem(THEME_KEY, theme)
    applyHtmlClass()
  }

  const isDark = computed(() => {
    return currentTheme.value === 'dark' || (currentTheme.value === 'system' && systemIsDark.value)
  })

  return {
    theme: currentTheme,
    isDark,
    setTheme,
    toggleTheme: () => setTheme(isDark.value ? 'light' : 'dark'),
  }
}
