<template>
  <PopoverRoot v-model:open="isOpen">
    <PopoverTrigger as-child>
      <div
        :id="triggerId"
        v-bind="restAttrs"
        role="combobox"
        tabindex="0"
        aria-haspopup="listbox"
        :aria-expanded="isOpen"
        :aria-invalid="isInvalid || undefined"
        :class="cn(
          controlBase,
          'flex min-h-9 flex-wrap items-center gap-1.5 rounded-lg py-1 pl-1.5 pr-2 text-left text-sm select-none cursor-pointer',
          isInvalid ? controlInvalid : (isOpen ? controlOpen : controlIdle),
          disabled && controlDisabled,
          $attrs.class
        )"
        @keydown.down.prevent="isOpen = true"
        @keydown.enter.prevent="isOpen = true"
        @keydown.backspace="handleBackspace"
      >
        <span v-if="!selectedList.length" class="px-1.5 text-muted">
          {{ placeholder }}
        </span>

        <template v-else>
          <span
            v-for="item in visibleChips"
            :key="getOptValue(item)"
            class="inline-flex max-w-full items-center gap-1 rounded-md border border-primary-200 bg-primary-50 py-0.5 pl-2 pr-1 text-xs font-medium text-primary-800 dark:border-primary-800 dark:bg-primary-950 dark:text-primary-200"
          >
            <span class="max-w-[160px] truncate">{{ getOptLabel(item) }}</span>
            <span
              role="button"
              tabindex="-1"
              class="rounded p-0.5 text-primary-500 transition hover:bg-primary-100 hover:text-primary-800 dark:hover:bg-primary-900"
              :aria-label="`Remove ${getOptLabel(item)}`"
              @click.stop.prevent="removeItem(getOptValue(item))"
            >
              <X class="h-3 w-3" />
            </span>
          </span>
          <span
            v-if="overflowCount > 0"
            class="inline-flex items-center rounded-md bg-muted px-1.5 py-0.5 text-[11px] font-semibold text-secondary"
          >
            +{{ overflowCount }}
          </span>
        </template>

        <span class="ml-auto flex shrink-0 items-center gap-1 pl-1">
          <Spinner v-if="isLoading && !isOpen" size="xs" class="text-muted" />
          <span
            v-if="clearable && selectedList.length > 0 && !disabled"
            role="button"
            tabindex="-1"
            class="rounded p-0.5 text-muted transition hover:bg-subtle hover:text-primary"
            aria-label="Clear all"
            @click.stop.prevent="clearAll"
          >
            <X class="h-3.5 w-3.5" />
          </span>
          <ChevronsUpDown class="h-4 w-4 text-muted" />
        </span>
      </div>
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        align="start"
        :side-offset="6"
        :collision-padding="12"
        :class="cn(
          floatingPanel,
          'z-dropdown flex w-[var(--reka-popover-trigger-width)] min-w-[260px] flex-col overflow-hidden',
          'max-h-[min(400px,var(--reka-popover-content-available-height))]'
        )"
        @open-auto-focus.prevent="focusSearch"
        @close-auto-focus="$emit('blur')"
      >
        <div class="flex items-center gap-2 border-b border-border-default px-3">
          <Search class="h-4 w-4 shrink-0 text-muted" />
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            class="h-10 w-full border-0 bg-transparent px-0 text-sm text-primary placeholder:text-muted outline-none focus:ring-0"
            placeholder="Search…"
            @input="onSearchInput"
            @keydown.down.prevent="navigate(1)"
            @keydown.up.prevent="navigate(-1)"
            @keydown.enter.prevent="toggleHighlighted"
          />
          <Spinner v-if="isLoading" size="xs" class="shrink-0 text-primary-600" />
        </div>

        <div ref="listRef" class="min-h-0 flex-1 overflow-y-auto p-1" role="listbox" aria-multiselectable="true">
          <div v-if="fetchError" class="p-4 text-center text-xs text-danger-600">
            <p>{{ fetchError }}</p>
            <button type="button" class="mt-1 font-medium text-primary-600 hover:underline" @click="fetchOptions">Retry</button>
          </div>

          <div v-else-if="isLoading && !displayedOptions.length" class="space-y-1 p-1">
            <div v-for="n in 4" :key="n" class="h-8 animate-pulse rounded-md bg-muted" />
          </div>

          <div v-else-if="!displayedOptions.length" class="px-3 py-6 text-center text-xs text-muted">
            {{ searchQuery ? `No results for “${searchQuery}”` : 'No options available' }}
          </div>

          <template v-else>
          <div
            v-for="(opt, idx) in displayedOptions"
            :key="getOptValue(opt)"
            role="option"
            :aria-selected="isItemSelected(opt)"
            :data-idx="idx"
            :class="cn(optionRow, highlighted === idx && 'bg-subtle')"
            @mouseenter="highlighted = idx"
            @mousedown.prevent
            @click="toggleItem(opt)"
          >
            <span
              :class="cn(
                'flex h-4 w-4 shrink-0 items-center justify-center rounded-[5px] border transition-colors',
                isItemSelected(opt)
                  ? 'border-primary-600 bg-primary-600 text-white dark:border-primary-500 dark:bg-primary-500'
                  : 'border-border-strong bg-surface'
              )"
            >
              <Check v-if="isItemSelected(opt)" class="h-3 w-3 stroke-[3]" />
            </span>
            <span class="min-w-0 flex-1 truncate">{{ getOptLabel(opt) }}</span>
          </div>
          </template>
        </div>

        <div class="flex items-center justify-between border-t border-border-default bg-subtle/60 px-3 py-2 text-xs">
          <button
            type="button"
            class="font-medium text-primary-600 hover:underline disabled:opacity-40 dark:text-primary-400"
            :disabled="!displayedOptions.length"
            @click="selectAllFiltered"
          >
            Select all ({{ displayedOptions.length }})
          </button>
          <span class="text-muted">{{ (modelValue || []).length }} selected</span>
          <button
            type="button"
            class="text-secondary hover:text-danger-600 hover:underline disabled:opacity-40"
            :disabled="!(modelValue || []).length"
            @click="clearAll"
          >
            Clear
          </button>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, inject, useAttrs } from 'vue'
import { PopoverRoot, PopoverTrigger, PopoverPortal, PopoverContent } from 'reka-ui'
import { Search, ChevronsUpDown, Check, X } from 'lucide-vue-next'
import api from '../../api'
import { cn } from '../../utils/cn'
import Spinner from './Spinner.vue'
import {
  controlBase, controlIdle, controlOpen, controlInvalid, controlDisabled, floatingPanel, optionRow,
} from './controlStyles'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  options: { type: Array, default: () => [] },
  resource: { type: String, default: '' },
  valueKey: { type: String, default: 'id' },
  labelKey: { type: String, default: 'display' },
  placeholder: { type: String, default: 'Select multiple…' },
  maxChips: { type: Number, default: 3 },
  disabled: { type: Boolean, default: false },
  invalid: { type: Boolean, default: false },
  error: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
  id: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'change', 'clear', 'blur'])

const attrs = useAttrs()
const restAttrs = computed(() => {
  const { class: _c, ...rest } = attrs
  return rest
})

const fieldCtx = inject('formField', null)
const triggerId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)
const isInvalid = computed(() => props.invalid || props.error || !!fieldCtx?.invalid?.value)

const searchInputRef = ref(null)
const listRef = ref(null)
const isOpen = ref(false)
const searchQuery = ref('')
const fetching = ref(false)
const fetchError = ref('')
const fetchedOptions = ref([])
const highlighted = ref(0)
let debounceTimer = null

const isLoading = computed(() => fetching.value || props.loading)

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

const allPool = computed(() => (props.resource ? fetchedOptions.value : props.options))

const displayedOptions = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q || props.resource) return allPool.value
  return allPool.value.filter((o) => getOptLabel(o).toLowerCase().includes(q))
})

const selectedSet = computed(() => new Set((props.modelValue || []).map(String)))

const selectedList = computed(() => allPool.value.filter((o) => selectedSet.value.has(String(getOptValue(o)))))
const visibleChips = computed(() => selectedList.value.slice(0, props.maxChips))
const overflowCount = computed(() => Math.max(0, selectedList.value.length - props.maxChips))

function isItemSelected(opt) {
  return selectedSet.value.has(String(getOptValue(opt)))
}

function emitValue(next) {
  emit('update:modelValue', next)
  emit('change', next)
}

function toggleItem(opt) {
  const val = getOptValue(opt)
  const current = [...(props.modelValue || [])]
  const idx = current.findIndex((v) => String(v) === String(val))
  if (idx >= 0) current.splice(idx, 1)
  else current.push(val)
  emitValue(current)
}

function removeItem(val) {
  emitValue((props.modelValue || []).filter((v) => String(v) !== String(val)))
}

function clearAll() {
  emitValue([])
  emit('clear')
}

function selectAllFiltered() {
  // Preserve the original value types (numbers stay numbers, strings stay strings).
  const current = [...(props.modelValue || [])]
  const seen = new Set(current.map(String))
  for (const o of displayedOptions.value) {
    const v = getOptValue(o)
    if (!seen.has(String(v))) {
      seen.add(String(v))
      current.push(v)
    }
  }
  emitValue(current)
}

function handleBackspace() {
  if (selectedList.value.length > 0 && !isOpen.value) {
    removeItem(getOptValue(selectedList.value[selectedList.value.length - 1]))
  }
}

function navigate(dir) {
  const len = displayedOptions.value.length
  if (!len) return
  highlighted.value = (highlighted.value + dir + len) % len
  nextTick(() => listRef.value?.querySelector(`[data-idx="${highlighted.value}"]`)?.scrollIntoView({ block: 'nearest' }))
}

function toggleHighlighted() {
  const opt = displayedOptions.value[highlighted.value]
  if (opt) toggleItem(opt)
}

function onSearchInput() {
  highlighted.value = 0
  if (props.resource) {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(fetchOptions, 250)
  }
}

async function fetchOptions() {
  if (!props.resource) return
  fetching.value = true
  fetchError.value = ''
  try {
    const res = await api.get(`${props.resource}/`, {
      params: { search: searchQuery.value || undefined, page_size: 100 },
    })
    fetchedOptions.value = res.data?.results || []
  } catch {
    fetchError.value = 'Failed to load options.'
  } finally {
    fetching.value = false
  }
}

function focusSearch() {
  nextTick(() => searchInputRef.value?.focus())
}

watch(isOpen, (open) => {
  if (open) highlighted.value = 0
  else searchQuery.value = ''
})

onMounted(() => {
  if (props.resource) fetchOptions()
})

onUnmounted(() => clearTimeout(debounceTimer))
</script>
