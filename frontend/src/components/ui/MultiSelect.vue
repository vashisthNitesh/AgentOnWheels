<template>
  <div ref="containerRef" class="relative w-full">
    <!-- Trigger Box -->
    <div
      :id="triggerId"
      tabindex="0"
      :aria-haspopup="'listbox'"
      :aria-expanded="isOpen"
      :class="cn(
        'w-full min-h-[36px] flex flex-wrap items-center gap-1.5 p-1.5 bg-surface text-primary border rounded-md transition text-left focus-ring select-none cursor-pointer',
        (invalid || fieldCtx?.invalid?.value)
          ? 'border-danger-500 ring-2 ring-danger-500/20'
          : 'border-border-strong hover:border-slate-400 dark:hover:border-slate-500 focus-within:border-primary-500',
        disabled && 'opacity-60 cursor-not-allowed bg-muted pointer-events-none',
        $attrs.class
      )"
      @click="toggleOpen"
      @keydown.down.prevent="openAndFocus"
      @keydown.backspace="handleBackspace"
      @keydown.esc="close"
    >
      <!-- Empty Placeholder -->
      <span v-if="!selectedList.length" class="text-muted text-xs px-1.5 select-none">
        {{ placeholder }}
      </span>

      <!-- Selected Chips -->
      <template v-else>
        <span
          v-for="item in visibleChips"
          :key="getOptValue(item)"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-subtle border border-border-default text-xs font-medium text-primary select-none"
        >
          <span class="truncate max-w-[140px]">{{ getOptLabel(item) }}</span>
          <button
            type="button"
            tabindex="-1"
            class="text-secondary hover:text-danger-600 transition p-0.5 rounded"
            aria-label="Remove item"
            @click.stop="removeItem(getOptValue(item))"
          >
            <X class="w-3 h-3" />
          </button>
        </span>

        <!-- +N more badge -->
        <span
          v-if="overflowCount > 0"
          class="inline-flex items-center px-1.5 py-0.5 rounded bg-muted text-[11px] font-semibold text-secondary"
        >
          +{{ overflowCount }} more
        </span>
      </template>

      <!-- Right Icons -->
      <div class="ml-auto flex items-center gap-1 pr-1 shrink-0">
        <button
          v-if="clearable && selectedList.length > 0 && !disabled"
          type="button"
          tabindex="-1"
          class="text-secondary hover:text-primary p-0.5 rounded transition"
          aria-label="Clear all"
          @click.stop="clearAll"
        >
          <X class="w-3.5 h-3.5" />
        </button>
        <ChevronDown :class="cn('w-4 h-4 text-secondary transition-transform shrink-0', isOpen && 'rotate-180')" />
      </div>
    </div>

    <!-- Dropdown Menu -->
    <div
      v-if="isOpen"
      ref="popoverRef"
      class="absolute left-0 top-full mt-1 z-dropdown w-full min-w-[260px] max-h-[340px] rounded-lg border border-border-default bg-surface-raised text-primary shadow-lg overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150"
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
          placeholder="Search items…"
          @input="onSearchInput"
        />
        <Spinner v-if="loading" size="xs" class="text-primary-600 shrink-0 mr-1" />
      </div>

      <!-- Items List -->
      <div class="overflow-y-auto p-1 max-h-[220px] flex-1">
        <div v-if="fetchError" class="p-3 text-center text-xs text-danger-600">
          <p>{{ fetchError }}</p>
          <button type="button" class="mt-1 text-primary-600 underline" @click="fetchOptions">Retry</button>
        </div>

        <div v-else-if="!loading && displayedOptions.length === 0" class="p-4 text-center text-xs text-muted">
          No results for "{{ searchQuery }}"
        </div>

        <div
          v-for="opt in displayedOptions"
          :key="getOptValue(opt)"
          :class="cn(
            'flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs cursor-pointer select-none transition-colors hover:bg-subtle',
            isItemSelected(opt) && 'bg-primary-50 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300 font-medium'
          )"
          @click="toggleItem(opt)"
        >
          <div
            :class="cn(
              'w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-colors',
              isItemSelected(opt)
                ? 'bg-primary-600 border-primary-600 text-white dark:bg-primary-500'
                : 'border-border-strong bg-surface'
            )"
          >
            <Check v-if="isItemSelected(opt)" class="w-3 h-3 stroke-[2.5]" />
          </div>
          <span class="truncate flex-1">{{ getOptLabel(opt) }}</span>
        </div>
      </div>

      <!-- Footer: Select All / Clear -->
      <div class="p-2 border-t border-border-default bg-subtle flex items-center justify-between text-xs">
        <button
          type="button"
          class="text-primary-600 dark:text-primary-400 hover:underline font-medium"
          @click="selectAllFiltered"
        >
          Select all ({{ displayedOptions.length }})
        </button>
        <button
          type="button"
          class="text-secondary hover:text-danger-600 hover:underline"
          @click="clearAll"
        >
          Clear
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, inject } from 'vue'
import { Search, ChevronDown, Check, X } from 'lucide-vue-next'
import { onClickOutside } from '@vueuse/core'
import api from '../../api'
import { cn } from '../../utils/cn'
import Spinner from './Spinner.vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  options: {
    type: Array,
    default: () => [],
  },
  resource: {
    type: String,
    default: '',
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
    default: 'Select multiple…',
  },
  maxChips: {
    type: Number,
    default: 3,
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
})

const emit = defineEmits(['update:modelValue', 'change', 'clear'])

const fieldCtx = inject('formField', null)
const triggerId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)

const containerRef = ref(null)
const searchInputRef = ref(null)

const isOpen = ref(false)
const searchQuery = ref('')
const loading = ref(false)
const fetchError = ref('')
const fetchedOptions = ref([])

onClickOutside(containerRef, () => {
  if (isOpen.value) close()
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
  if (props.resource) return fetchedOptions.value
  return props.options
})

const displayedOptions = computed(() => {
  const pool = allPool.value
  if (!searchQuery.value.trim()) return pool
  const q = searchQuery.value.toLowerCase().trim()
  return pool.filter(o => getOptLabel(o).toLowerCase().includes(q))
})

const selectedList = computed(() => {
  const selectedVals = (props.modelValue || []).map(String)
  return allPool.value.filter(o => selectedVals.includes(String(getOptValue(o))))
})

const visibleChips = computed(() => {
  return selectedList.value.slice(0, props.maxChips)
})

const overflowCount = computed(() => {
  return Math.max(0, selectedList.value.length - props.maxChips)
})

function isItemSelected(opt) {
  const val = String(getOptValue(opt))
  return (props.modelValue || []).map(String).includes(val)
}

function toggleItem(opt) {
  const val = getOptValue(opt)
  const current = [...(props.modelValue || [])]
  const idx = current.findIndex(v => String(v) === String(val))
  if (idx >= 0) {
    current.splice(idx, 1)
  } else {
    current.push(val)
  }
  emit('update:modelValue', current)
  emit('change', current)
}

function removeItem(val) {
  const current = (props.modelValue || []).filter(v => String(v) !== String(val))
  emit('update:modelValue', current)
  emit('change', current)
}

function clearAll() {
  emit('update:modelValue', [])
  emit('change', [])
  emit('clear')
}

function selectAllFiltered() {
  const current = new Set((props.modelValue || []).map(String))
  displayedOptions.value.forEach(o => current.add(String(getOptValue(o))))
  const updated = Array.from(current).map(Number)
  emit('update:modelValue', updated)
  emit('change', updated)
}

function handleBackspace() {
  if (selectedList.value.length > 0 && !searchQuery.value) {
    const last = selectedList.value[selectedList.value.length - 1]
    removeItem(getOptValue(last))
  }
}

let debounceTimer = null
function onSearchInput() {
  if (props.resource) {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      fetchOptions()
    }, 250)
  }
}

async function fetchOptions() {
  if (!props.resource) return
  loading.value = true
  fetchError.value = ''
  try {
    const res = await api.get(`${props.resource}/`, {
      params: { search: searchQuery.value || undefined, page_size: 100 },
    })
    fetchedOptions.value = res.data?.results || []
  } catch (err) {
    fetchError.value = 'Failed to load options.'
  } finally {
    loading.value = false
  }
}

function toggleOpen() {
  if (isOpen.value) close()
  else openAndFocus()
}

function openAndFocus() {
  isOpen.value = true
  if (props.resource && fetchedOptions.value.length === 0) {
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

onMounted(() => {
  if (props.resource) {
    fetchOptions()
  }
})
</script>
