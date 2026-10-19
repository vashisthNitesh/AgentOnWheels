<template>
  <div ref="containerRef" :class="cn('relative w-full', isOpen && 'z-50')">
    <!-- Trigger Button -->
    <button
      type="button"
      :id="triggerId"
      :disabled="disabled"
      :aria-haspopup="'listbox'"
      :aria-expanded="isOpen"
      :aria-invalid="invalid || fieldCtx?.invalid?.value"
      :aria-describedby="ariaDescribedby || fieldCtx?.describedBy?.value"
      :class="cn(
        'w-full flex items-center justify-between bg-surface text-primary border rounded-md transition text-left focus-ring select-none',
        sizeClasses,
        (invalid || fieldCtx?.invalid?.value)
          ? 'border-danger-500 focus:border-danger-500 ring-2 ring-danger-500/20'
          : 'border-border-strong hover:border-slate-400 dark:hover:border-slate-500 focus:border-primary-500',
        disabled && 'opacity-60 cursor-not-allowed bg-muted pointer-events-none',
        $attrs.class
      )"
      @click="toggleOpen"
      @keydown.down.prevent="openAndFocus"
      @keydown.esc="close"
    >
      <span class="truncate block flex-1">
        <span v-if="selectedDisplay" class="font-medium text-primary">{{ selectedDisplay }}</span>
        <span v-else class="text-muted font-normal">{{ placeholder }}</span>
      </span>

      <div class="flex items-center gap-1 ml-2 shrink-0">
        <button
          v-if="clearable && modelValue !== null && modelValue !== undefined && modelValue !== '' && !disabled"
          type="button"
          tabindex="-1"
          class="text-secondary hover:text-primary p-0.5 rounded transition"
          aria-label="Clear selection"
          @click.stop="clearSelection"
        >
          <X class="w-3.5 h-3.5" />
        </button>
        <ChevronDown :class="cn('w-4 h-4 text-secondary transition-transform shrink-0', isOpen && 'rotate-180')" />
      </div>
    </button>

    <!-- Dropdown Popover Menu -->
    <div
      v-if="isOpen"
      ref="popoverRef"
      :class="cn(
        'absolute left-0 z-dropdown w-full min-w-[240px] max-h-[340px] rounded-lg border border-border-default bg-surface-raised bg-white dark:bg-slate-900 text-primary shadow-xl shadow-slate-950/15 dark:shadow-black/60 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150',
        openUpward ? 'bottom-full mb-1' : 'top-full mt-1'
      )"
      @keydown.esc="close"
    >
      <!-- Search Input -->
      <div class="p-2 border-b border-border-default flex items-center gap-2 bg-subtle">
        <Search class="w-4 h-4 text-muted shrink-0 ml-1" />
        <input
          ref="searchInputRef"
          v-model="searchQuery"
          type="text"
          class="w-full bg-transparent text-xs text-primary placeholder:text-muted focus:outline-none"
          :placeholder="searchPlaceholder || 'Search…'"
          @input="onSearchInput"
          @keydown.down.prevent="navigateHighlight(1)"
          @keydown.up.prevent="navigateHighlight(-1)"
          @keydown.enter.prevent="selectHighlighted"
        />
        <Spinner v-if="loading" size="xs" class="text-primary-600 shrink-0 mr-1" />
      </div>

      <!-- Options List -->
      <div class="overflow-y-auto p-1 max-h-[260px] flex-1">
        <!-- Error State with Retry -->
        <div v-if="fetchError" class="p-3 text-center text-xs text-danger-600">
          <p>{{ fetchError }}</p>
          <button type="button" class="mt-1 text-primary-600 underline" @click="fetchOptions">Retry</button>
        </div>

        <!-- Empty State -->
        <div v-else-if="!loading && displayedOptions.length === 0" class="p-4 text-center text-xs text-muted">
          <span>No results for "{{ searchQuery }}"</span>
          <div v-if="createable && searchQuery.trim()" class="mt-2">
            <button
              type="button"
              class="inline-flex items-center gap-1 text-xs text-primary-600 hover:underline"
              @click="handleCreate"
            >
              <Plus class="w-3 h-3" /> Create "{{ searchQuery.trim() }}"
            </button>
          </div>
        </div>

        <!-- Options Render -->
        <template v-else>
          <!-- Recent Items Section if no query -->
          <div v-if="!searchQuery && recentOptions.length > 0" class="mb-2 pb-2 border-b border-border-default">
            <div class="px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-muted">Recent</div>
            <div
              v-for="(opt, idx) in recentOptions"
              :key="'recent-' + getOptValue(opt)"
              :class="cn(
                'flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs cursor-pointer select-none transition-colors',
                highlightedIndex === idx ? 'bg-subtle text-primary' : 'hover:bg-subtle',
                isSelected(opt) && 'bg-primary-50 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300'
              )"
              @mouseenter="highlightedIndex = idx"
              @click="selectOption(opt)"
            >
              <span class="truncate">{{ getOptLabel(opt) }}</span>
              <Check v-if="isSelected(opt)" class="w-3.5 h-3.5 text-primary-600 shrink-0 ml-2" />
            </div>
          </div>

          <!-- All / Filtered Items -->
          <div
            v-for="(opt, idx) in displayedOptions"
            :key="getOptValue(opt)"
            :class="cn(
              'flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs cursor-pointer select-none transition-colors',
              highlightedIndex === idx ? 'bg-subtle text-primary' : 'hover:bg-subtle',
              isSelected(opt) && 'bg-primary-50 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300'
            )"
            @mouseenter="highlightedIndex = idx"
            @click="selectOption(opt)"
          >
            <div class="flex items-center gap-2 truncate">
              <span class="truncate font-medium">{{ getOptLabel(opt) }}</span>
              <span v-if="opt.code || opt.plate_number || opt.asset_code" class="font-mono text-[11px] text-muted">
                {{ opt.code || opt.plate_number || opt.asset_code }}
              </span>
            </div>
            <Check v-if="isSelected(opt)" class="w-3.5 h-3.5 text-primary-600 shrink-0 ml-2" />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, inject } from 'vue'
import { Search, ChevronDown, Check, X, Plus } from 'lucide-vue-next'
import { onClickOutside } from '@vueuse/core'
import api from '../../api'
import { cn } from '../../utils/cn'
import Spinner from './Spinner.vue'

const props = defineProps({
  modelValue: {
    type: [Number, String, Object, null],
    default: null,
  },
  options: {
    type: Array,
    default: () => [],
  },
  resource: {
    type: String,
    default: '',
  },
  loadOptions: {
    type: Function,
    default: null,
  },
  valueKey: {
    type: String,
    default: 'id',
  },
  labelKey: {
    type: String,
    default: 'display',
  },
  placeholder: {
    type: String,
    default: 'Select…',
  },
  searchPlaceholder: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg'].includes(v),
  },
  debounce: {
    type: Number,
    default: 250,
  },
  minChars: {
    type: Number,
    default: 0,
  },
  initialOption: {
    type: Object,
    default: null,
  },
  createable: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  invalid: {
    type: Boolean,
    default: false,
  },
  clearable: {
    type: Boolean,
    default: true,
  },
  id: {
    type: String,
    default: '',
  },
  ariaDescribedby: {
    type: String,
    default: undefined,
  },
})

const emit = defineEmits(['update:modelValue', 'change', 'create', 'clear'])

const fieldCtx = inject('formField', null)
const triggerId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)

const containerRef = ref(null)
const popoverRef = ref(null)
const searchInputRef = ref(null)

const isOpen = ref(false)
const searchQuery = ref('')
const loading = ref(false)
const fetchError = ref('')
const fetchedOptions = ref([])
const highlightedIndex = ref(0)
const abortController = ref(null)
const recentKeys = ref([])
const openUpward = ref(false)

function checkPosition() {
  if (!containerRef.value || typeof window === 'undefined') return
  const rect = containerRef.value.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom
  openUpward.value = spaceBelow < 340 && rect.top > 340
}

onClickOutside(containerRef, () => {
  if (isOpen.value) close()
})

const sizeClasses = computed(() => {
  return {
    sm: 'h-8 text-xs px-2.5',
    md: 'h-9 text-sm px-3',
    lg: 'h-10 text-base px-3.5',
  }[props.size]
})

function getOptValue(opt) {
  if (typeof opt === 'object' && opt !== null) {
    return opt[props.valueKey] ?? opt.value ?? opt.id
  }
  return opt
}

function getOptLabel(opt) {
  if (typeof opt === 'object' && opt !== null) {
    return opt[props.labelKey] ?? opt.label ?? opt.name ?? opt.display ?? String(getOptValue(opt))
  }
  return String(opt)
}

const allPool = computed(() => {
  if (props.resource || props.loadOptions) {
    return fetchedOptions.value
  }
  return props.options
})

const displayedOptions = computed(() => {
  const pool = allPool.value
  if (!searchQuery.value.trim()) return pool
  const q = searchQuery.value.toLowerCase().trim()
  return pool.filter(o => getOptLabel(o).toLowerCase().includes(q))
})

const recentOptions = computed(() => {
  if (!recentKeys.value.length || !allPool.value.length) return []
  return allPool.value.filter(o => recentKeys.value.includes(String(getOptValue(o))))
})

const selectedOption = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '') return null
  const targetVal = String(props.modelValue)

  // Check in current pool
  const match = allPool.value.find(o => String(getOptValue(o)) === targetVal)
  if (match) return match

  // Check initial option
  if (props.initialOption && String(getOptValue(props.initialOption)) === targetVal) {
    return props.initialOption
  }

  return null
})

const selectedDisplay = computed(() => {
  if (selectedOption.value) return getOptLabel(selectedOption.value)
  if (props.modelValue !== null && props.modelValue !== undefined && props.modelValue !== '') {
    return String(props.modelValue)
  }
  return ''
})

function isSelected(opt) {
  if (props.modelValue === null || props.modelValue === undefined) return false
  return String(getOptValue(opt)) === String(props.modelValue)
}

let debounceTimer = null

function onSearchInput() {
  highlightedIndex.value = 0
  if (props.resource || props.loadOptions) {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      fetchOptions()
    }, props.debounce)
  }
}

async function fetchOptions() {
  if (abortController.value) {
    abortController.value.abort()
  }
  abortController.value = new AbortController()
  const signal = abortController.value.signal

  loading.value = true
  fetchError.value = ''

  try {
    if (props.loadOptions) {
      const res = await props.loadOptions(searchQuery.value, { signal, page: 1 })
      fetchedOptions.value = res || []
    } else if (props.resource) {
      const res = await api.get(`${props.resource}/`, {
        params: {
          search: searchQuery.value || undefined,
          page_size: 50,
        },
        signal,
      })
      fetchedOptions.value = res.data?.results || []
    }
  } catch (err) {
    if (err.name !== 'CanceledError' && err.code !== 'ERR_CANCELED') {
      fetchError.value = 'Failed to load options.'
      console.error(err)
    }
  } finally {
    loading.value = false
  }
}

function toggleOpen() {
  if (isOpen.value) close()
  else openAndFocus()
}

function openAndFocus() {
  checkPosition()
  isOpen.value = true
  highlightedIndex.value = 0
  if ((props.resource || props.loadOptions) && fetchedOptions.value.length === 0) {
    fetchOptions()
  }
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

function close() {
  isOpen.value = false
  searchQuery.value = ''
}

function selectOption(opt) {
  const val = getOptValue(opt)
  emit('update:modelValue', val)
  emit('change', opt)

  // Save to recent
  const sVal = String(val)
  recentKeys.value = [sVal, ...recentKeys.value.filter(k => k !== sVal)].slice(0, 5)
  try {
    localStorage.setItem(`aow_recent_${props.resource || 'cb'}`, JSON.stringify(recentKeys.value))
  } catch {}

  close()
}

function clearSelection() {
  emit('update:modelValue', null)
  emit('change', null)
  emit('clear')
}

function navigateHighlight(dir) {
  const len = displayedOptions.value.length
  if (len === 0) return
  highlightedIndex.value = (highlightedIndex.value + dir + len) % len
}

function selectHighlighted() {
  if (displayedOptions.value[highlightedIndex.value]) {
    selectOption(displayedOptions.value[highlightedIndex.value])
  } else if (props.createable && searchQuery.value.trim()) {
    handleCreate()
  }
}

function handleCreate() {
  emit('create', searchQuery.value.trim())
  close()
}

onMounted(() => {
  try {
    const saved = localStorage.getItem(`aow_recent_${props.resource || 'cb'}`)
    if (saved) recentKeys.value = JSON.parse(saved)
  } catch {}
  if (props.resource && props.modelValue) {
    fetchOptions()
  }
})

onUnmounted(() => {
  if (abortController.value) {
    abortController.value.abort()
  }
})
</script>
