<template>
  <PopoverRoot v-model:open="isOpen">
    <PopoverTrigger as-child>
      <button
        :id="triggerId"
        type="button"
        v-bind="restAttrs"
        :disabled="disabled"
        aria-haspopup="listbox"
        :aria-expanded="isOpen"
        :aria-invalid="isInvalid || undefined"
        :aria-describedby="ariaDescribedby || fieldCtx?.describedBy?.value"
        :class="cn(
          controlBase,
          'flex items-center justify-between gap-2 text-left select-none cursor-pointer',
          controlSizes[size],
          isInvalid ? controlInvalid : (isOpen ? controlOpen : controlIdle),
          disabled && controlDisabled,
          $attrs.class
        )"
        @keydown.down.prevent="isOpen = true"
      >
        <span class="block min-w-0 flex-1 truncate">
          <span v-if="selectedDisplay" class="text-primary">{{ selectedDisplay }}</span>
          <span v-else class="text-muted">{{ placeholder }}</span>
        </span>

        <span class="flex shrink-0 items-center gap-1">
          <Spinner v-if="isLoading && !isOpen" size="xs" class="text-muted" />
          <span
            v-if="clearable && hasValue && !disabled"
            role="button"
            tabindex="-1"
            class="rounded p-0.5 text-muted transition hover:bg-subtle hover:text-primary"
            aria-label="Clear selection"
            @click.stop.prevent="clearSelection"
          >
            <X class="h-3.5 w-3.5" />
          </span>
          <ChevronsUpDown class="h-4 w-4 text-muted" />
        </span>
      </button>
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        align="start"
        :side-offset="6"
        :collision-padding="12"
        :class="cn(
          floatingPanel,
          'z-dropdown flex w-[var(--reka-popover-trigger-width)] min-w-[240px] flex-col overflow-hidden',
          'max-h-[min(380px,var(--reka-popover-content-available-height))]'
        )"
        @open-auto-focus.prevent="focusSearch"
        @close-auto-focus="$emit('blur')"
      >
        <!-- Search -->
        <div class="flex items-center gap-2 border-b border-border-default px-3">
          <Search class="h-4 w-4 shrink-0 text-muted" />
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            class="h-10 w-full bg-transparent text-sm text-primary placeholder:text-muted outline-none border-0 focus:ring-0 px-0"
            :placeholder="searchPlaceholder || 'Search…'"
            role="combobox"
            aria-autocomplete="list"
            :aria-activedescendant="highlightedId"
            @input="onSearchInput"
            @keydown.down.prevent="navigateHighlight(1)"
            @keydown.up.prevent="navigateHighlight(-1)"
            @keydown.enter.prevent="selectHighlighted"
            @keydown.tab="isOpen = false"
          />
          <Spinner v-if="isLoading" size="xs" class="shrink-0 text-primary-600" />
        </div>

        <!-- Options -->
        <div ref="listRef" class="min-h-0 flex-1 overflow-y-auto p-1" role="listbox">
          <div v-if="fetchError" class="p-4 text-center text-xs text-danger-600">
            <p>{{ fetchError }}</p>
            <button type="button" class="mt-1 font-medium text-primary-600 hover:underline" @click="fetchOptions">
              Retry
            </button>
          </div>

          <div v-else-if="isLoading && !flatItems.length" class="space-y-1 p-1">
            <div v-for="n in 4" :key="n" class="h-8 animate-pulse rounded-md bg-muted" />
          </div>

          <div v-else-if="!flatItems.length" class="px-3 py-6 text-center text-xs text-muted">
            <span>{{ searchQuery ? `No results for “${searchQuery}”` : 'No options available' }}</span>
            <div v-if="createable && searchQuery.trim()" class="mt-2">
              <button
                type="button"
                class="inline-flex items-center gap-1 text-xs font-medium text-primary-600 hover:underline"
                @click="handleCreate"
              >
                <Plus class="h-3 w-3" /> Create “{{ searchQuery.trim() }}”
              </button>
            </div>
          </div>

          <template v-else>
            <template v-for="(item, idx) in flatItems" :key="item.key">
              <div
                v-if="item.heading"
                class="px-2.5 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wider text-muted"
              >
                {{ item.heading }}
              </div>
              <div
                :id="`${uid}-opt-${idx}`"
                role="option"
                :aria-selected="isSelected(item.opt)"
                :data-idx="idx"
                :class="cn(
                  optionRow,
                  'justify-between',
                  highlightedIndex === idx ? 'bg-subtle' : '',
                  isSelected(item.opt) && 'font-medium text-primary-700 dark:text-primary-300',
                  size === 'sm' && 'py-1.5 text-xs'
                )"
                @mouseenter="highlightedIndex = idx"
                @mousedown.prevent
                @click="selectOption(item.opt)"
              >
                <span class="flex min-w-0 items-center gap-2">
                  <span class="truncate">{{ getOptLabel(item.opt) }}</span>
                  <span
                    v-if="getOptMeta(item.opt)"
                    class="shrink-0 font-mono text-[11px] text-muted"
                  >
                    {{ getOptMeta(item.opt) }}
                  </span>
                </span>
                <Check v-if="isSelected(item.opt)" class="h-4 w-4 shrink-0 text-primary-600 dark:text-primary-400" />
              </div>
            </template>
          </template>
        </div>

        <div
          v-if="allPool.length > 0 && !fetchError"
          class="flex items-center justify-between border-t border-border-default bg-subtle/60 px-3 py-1.5 text-[11px] text-muted"
        >
          <span>{{ displayedOptions.length }} of {{ allPool.length }}</span>
          <span class="hidden sm:inline">↑↓ to navigate · Enter to select</span>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, inject, useAttrs } from 'vue'
import { PopoverRoot, PopoverTrigger, PopoverPortal, PopoverContent } from 'reka-ui'
import { Search, ChevronsUpDown, Check, X, Plus } from 'lucide-vue-next'
import api from '../../api'
import { cn } from '../../utils/cn'
import Spinner from './Spinner.vue'
import {
  controlBase, controlSizes, controlIdle, controlOpen, controlInvalid, controlDisabled,
  floatingPanel, optionRow,
} from './controlStyles'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: { type: [Number, String, Object, null], default: null },
  options: { type: Array, default: () => [] },
  resource: { type: String, default: '' },
  loadOptions: { type: Function, default: null },
  valueKey: { type: String, default: 'id' },
  labelKey: { type: String, default: 'display' },
  placeholder: { type: String, default: 'Select…' },
  searchPlaceholder: { type: String, default: '' },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg'].includes(v),
  },
  debounce: { type: Number, default: 250 },
  initialOption: { type: Object, default: null },
  createable: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  invalid: { type: Boolean, default: false },
  error: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
  id: { type: String, default: '' },
  ariaDescribedby: { type: String, default: undefined },
})

const emit = defineEmits(['update:modelValue', 'change', 'create', 'clear', 'blur'])

const attrs = useAttrs()
const restAttrs = computed(() => {
  const { class: _c, ...rest } = attrs
  return rest
})

const fieldCtx = inject('formField', null)
const triggerId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)
const isInvalid = computed(() => props.invalid || props.error || !!fieldCtx?.invalid?.value)
const uid = `cb-${Math.random().toString(36).slice(2, 8)}`

const searchInputRef = ref(null)
const listRef = ref(null)
const isOpen = ref(false)
const searchQuery = ref('')
const fetching = ref(false)
const fetchError = ref('')
const fetchedOptions = ref([])
const highlightedIndex = ref(0)
const recentKeys = ref([])
let abortController = null
let debounceTimer = null

const isRemote = computed(() => Boolean(props.resource || props.loadOptions))
const isLoading = computed(() => fetching.value || props.loading)
const recentStorageKey = computed(() => `aow_recent_${props.resource || props.id || 'cb'}`)

function getOptValue(opt) {
  if (typeof opt === 'object' && opt !== null) return opt[props.valueKey] ?? opt.value ?? opt.id
  return opt
}

function getOptLabel(opt) {
  if (typeof opt === 'object' && opt !== null) {
    return opt[props.labelKey] ?? opt.label ?? opt.name ?? opt.display ?? String(getOptValue(opt))
  }
  return String(opt)
}

function getOptMeta(opt) {
  if (typeof opt !== 'object' || opt === null) return ''
  return opt.code || opt.plate_number || opt.asset_code || ''
}

const allPool = computed(() => (isRemote.value ? fetchedOptions.value : props.options))

const displayedOptions = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  // Remote sources are filtered server-side.
  if (!q || isRemote.value) return allPool.value
  return allPool.value.filter((o) => {
    const label = getOptLabel(o).toLowerCase()
    const meta = String(getOptMeta(o)).toLowerCase()
    return label.includes(q) || meta.includes(q)
  })
})

// Flat list used for rendering and keyboard navigation (recent items first).
const flatItems = computed(() => {
  const items = []
  const showRecent = !searchQuery.value && recentKeys.value.length && allPool.value.length > 8
  const recentSet = new Set()
  if (showRecent) {
    const recents = recentKeys.value
      .map((k) => allPool.value.find((o) => String(getOptValue(o)) === k))
      .filter(Boolean)
    recents.forEach((opt, i) => {
      recentSet.add(String(getOptValue(opt)))
      items.push({ key: `r-${getOptValue(opt)}`, opt, heading: i === 0 ? 'Recent' : null })
    })
  }
  let first = true
  for (const opt of displayedOptions.value) {
    if (recentSet.has(String(getOptValue(opt)))) continue
    items.push({
      key: `o-${getOptValue(opt)}`,
      opt,
      heading: recentSet.size && first ? 'All' : null,
    })
    first = false
  }
  return items
})

const highlightedId = computed(() => (flatItems.value.length ? `${uid}-opt-${highlightedIndex.value}` : undefined))

const hasValue = computed(() => props.modelValue !== null && props.modelValue !== undefined && props.modelValue !== '')

const selectedOption = computed(() => {
  if (!hasValue.value) return null
  const target = String(props.modelValue)
  const match = allPool.value.find((o) => String(getOptValue(o)) === target)
  if (match) return match
  if (props.initialOption && String(getOptValue(props.initialOption)) === target) return props.initialOption
  return null
})

const selectedDisplay = computed(() => {
  if (selectedOption.value) return getOptLabel(selectedOption.value)
  if (hasValue.value) return isLoading.value ? 'Loading…' : `#${props.modelValue}`
  return ''
})

function isSelected(opt) {
  return hasValue.value && String(getOptValue(opt)) === String(props.modelValue)
}

function onSearchInput() {
  highlightedIndex.value = 0
  if (isRemote.value) {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(fetchOptions, props.debounce)
  }
}

async function fetchOptions() {
  abortController?.abort()
  abortController = new AbortController()
  const signal = abortController.signal
  fetching.value = true
  fetchError.value = ''
  try {
    if (props.loadOptions) {
      fetchedOptions.value = (await props.loadOptions(searchQuery.value, { signal, page: 1 })) || []
    } else if (props.resource) {
      const res = await api.get(`${props.resource}/`, {
        params: { search: searchQuery.value || undefined, page_size: 50 },
        signal,
      })
      fetchedOptions.value = res.data?.results || []
    }
  } catch (err) {
    if (err?.name !== 'CanceledError' && err?.code !== 'ERR_CANCELED') {
      fetchError.value = 'Failed to load options.'
    }
  } finally {
    fetching.value = false
  }
}

function focusSearch() {
  nextTick(() => searchInputRef.value?.focus())
}

watch(isOpen, (open) => {
  if (open) {
    const selIdx = flatItems.value.findIndex((i) => isSelected(i.opt))
    highlightedIndex.value = selIdx >= 0 ? selIdx : 0
    if (isRemote.value && fetchedOptions.value.length === 0) fetchOptions()
    nextTick(scrollHighlightedIntoView)
  } else {
    searchQuery.value = ''
    if (isRemote.value && fetchedOptions.value.length && debounceTimer) {
      clearTimeout(debounceTimer)
    }
  }
})

function scrollHighlightedIntoView() {
  const el = listRef.value?.querySelector(`[data-idx="${highlightedIndex.value}"]`)
  el?.scrollIntoView({ block: 'nearest' })
}

function navigateHighlight(dir) {
  const len = flatItems.value.length
  if (!len) return
  highlightedIndex.value = (highlightedIndex.value + dir + len) % len
  nextTick(scrollHighlightedIntoView)
}

function selectOption(opt) {
  const val = getOptValue(opt)
  emit('update:modelValue', val)
  emit('change', opt)
  const sVal = String(val)
  recentKeys.value = [sVal, ...recentKeys.value.filter((k) => k !== sVal)].slice(0, 5)
  try {
    localStorage.setItem(recentStorageKey.value, JSON.stringify(recentKeys.value))
  } catch {}
  isOpen.value = false
}

function selectHighlighted() {
  const item = flatItems.value[highlightedIndex.value]
  if (item) selectOption(item.opt)
  else if (props.createable && searchQuery.value.trim()) handleCreate()
}

function clearSelection() {
  emit('update:modelValue', null)
  emit('change', null)
  emit('clear')
}

function handleCreate() {
  emit('create', searchQuery.value.trim())
  isOpen.value = false
}

onMounted(() => {
  try {
    const saved = localStorage.getItem(recentStorageKey.value)
    if (saved) recentKeys.value = JSON.parse(saved)
  } catch {}
  if (props.resource && hasValue.value) fetchOptions()
})

onUnmounted(() => {
  abortController?.abort()
  clearTimeout(debounceTimer)
})
</script>
