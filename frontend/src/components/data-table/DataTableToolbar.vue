<template>
  <div>
    <!-- Status tabs -->
    <div
      v-if="statusTabs?.length > 1"
      class="flex items-center gap-1 overflow-x-auto border-b border-border-default px-2 scrollbar-none sm:px-3"
      role="tablist"
      aria-label="Filter by status"
    >
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        type="button"
        role="tab"
        :aria-selected="status === tab.value"
        :class="cn(
          'relative flex shrink-0 items-center gap-2 whitespace-nowrap px-2.5 pb-2.5 pt-3 text-[13px] font-medium transition-colors focus-visible:outline-none',
          'after:absolute after:inset-x-1.5 after:bottom-0 after:h-0.5 after:rounded-full after:transition-colors',
          status === tab.value
            ? 'text-primary after:bg-primary-600 dark:after:bg-primary-400'
            : 'text-muted hover:text-primary after:bg-transparent hover:after:bg-border-strong'
        )"
        @click="$emit('update:status', tab.value)"
      >
        <span>{{ tab.label }}</span>
        <span
          v-if="counts"
          :class="cn(
            'min-w-[1.25rem] rounded-full px-1.5 py-px text-center text-[11px] font-semibold tabular-nums',
            status === tab.value
              ? 'bg-primary-100 text-primary-700 dark:bg-primary-950 dark:text-primary-300'
              : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
          )"
        >
          {{ countFor(tab.value) }}
        </span>
      </button>
    </div>

    <!-- Main toolbar -->
    <div class="flex flex-wrap items-center gap-2 p-2.5 sm:px-3">
      <!-- Search -->
      <div class="relative min-w-0 flex-1 basis-full sm:basis-auto sm:max-w-sm">
        <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
        <input
          ref="searchRef"
          :value="localSearch"
          type="search"
          placeholder="Search…"
          aria-label="Search records"
          class="h-9 w-full rounded-lg border border-border-strong bg-surface pl-9 pr-16 text-sm text-primary shadow-xs outline-none transition placeholder:text-muted hover:border-slate-400 focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15 dark:hover:border-slate-500 [&::-webkit-search-cancel-button]:hidden"
          @input="onSearchInput"
          @keydown.esc.prevent="clearSearch"
        />
        <span class="absolute right-2 top-1/2 flex -translate-y-1/2 items-center gap-1">
          <Loader2 v-if="isFetching && localSearch" class="h-4 w-4 animate-spin text-primary-600" />
          <button
            v-else-if="localSearch"
            type="button"
            class="rounded p-0.5 text-muted hover:bg-subtle hover:text-primary"
            aria-label="Clear search"
            @click="clearSearch"
          >
            <X class="h-3.5 w-3.5" />
          </button>
          <Kbd v-else class="hidden sm:inline-flex">/</Kbd>
        </span>
      </div>

      <!-- Filters -->
      <button
        type="button"
        :class="cn(
          toolBtn,
          activeFiltersCount > 0 && 'border-primary-300 bg-primary-50 text-primary-700 hover:bg-primary-100 dark:border-primary-800 dark:bg-primary-950 dark:text-primary-300'
        )"
        @click="$emit('open-filters')"
      >
        <ListFilter class="h-4 w-4" />
        <span>Filters</span>
        <span
          v-if="activeFiltersCount > 0"
          class="rounded-full bg-primary-600 px-1.5 text-[11px] font-semibold leading-[18px] text-white dark:bg-primary-500"
        >
          {{ activeFiltersCount }}
        </span>
      </button>

      <!-- Saved views -->
      <Popover v-model:open="viewsOpen" align="start" class="w-72 p-0">
        <template #trigger>
          <button type="button" :class="toolBtn" title="Saved views">
            <Bookmark class="h-4 w-4" />
            <span class="max-w-[120px] truncate">{{ activeViewName || 'Views' }}</span>
            <span v-if="isViewModified && activeViewName" class="h-1.5 w-1.5 rounded-full bg-amber-500" title="Unsaved changes" />
            <ChevronDown class="h-3.5 w-3.5 opacity-60" />
          </button>
        </template>

        <div class="border-b border-border-default px-3 py-2.5">
          <p class="text-xs font-semibold text-primary">Saved views</p>
          <p class="text-[11px] text-muted">Filters, sort, columns and density.</p>
        </div>
        <div class="max-h-60 overflow-y-auto p-1">
          <div v-if="!savedViews.length" class="px-3 py-4 text-center text-xs text-muted">
            No saved views yet.
          </div>
          <div
            v-for="v in savedViews"
            :key="v.id"
            :class="cn(
              'group flex items-center justify-between gap-2 rounded-md px-2.5 py-1.5 text-[13px] transition-colors hover:bg-subtle',
              v.id === activeViewId && 'font-medium text-primary-700 dark:text-primary-300'
            )"
          >
            <button type="button" class="flex min-w-0 flex-1 items-center gap-2 text-left" @click="applyView(v)">
              <Check :class="cn('h-4 w-4 shrink-0', v.id === activeViewId ? 'opacity-100' : 'opacity-0')" />
              <span class="truncate">{{ v.name }}</span>
            </button>
            <button
              type="button"
              class="rounded p-1 text-muted opacity-0 transition hover:bg-danger-50 hover:text-danger-600 group-hover:opacity-100 focus-visible:opacity-100 dark:hover:bg-danger-500/10"
              :aria-label="`Delete view ${v.name}`"
              @click="$emit('delete-view', v.id)"
            >
              <Trash2 class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
        <form class="flex items-center gap-2 border-t border-border-default p-2" @submit.prevent="saveView">
          <input
            v-model="newViewName"
            type="text"
            maxlength="40"
            placeholder="Save current as…"
            class="h-8 min-w-0 flex-1 rounded-md border border-border-strong bg-surface px-2.5 text-xs text-primary outline-none placeholder:text-muted focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15"
          />
          <Button type="submit" size="sm" :disabled="!newViewName.trim()">Save</Button>
        </form>
      </Popover>

      <div class="ml-auto flex items-center gap-1.5">
        <DataTableColumnChooser
          :columns="allColumns"
          :hidden-columns="hiddenColumns"
          :column-order="columnOrder"
          :has-custom-widths="hasCustomWidths"
          @update:hidden-columns="$emit('update:hiddenColumns', $event)"
          @update:column-order="$emit('update:columnOrder', $event)"
          @reset="$emit('reset-columns')"
        />

        <DropdownMenu :items="densityItems" align="end">
          <template #trigger>
            <button type="button" :class="toolIconBtn" title="Row density" aria-label="Row density">
              <component :is="densityIcon" class="h-4 w-4" />
            </button>
          </template>
        </DropdownMenu>

        <Tooltip content="Export CSV">
          <button
            type="button"
            :disabled="isExporting"
            :class="toolIconBtn"
            aria-label="Export CSV"
            @click="$emit('export')"
          >
            <Loader2 v-if="isExporting" class="h-4 w-4 animate-spin text-primary-600" />
            <Download v-else class="h-4 w-4" />
          </button>
        </Tooltip>

        <Tooltip :content="`Refresh · updated ${relativeUpdated}`">
          <button
            type="button"
            :disabled="isFetching"
            :class="toolIconBtn"
            aria-label="Refresh"
            @click="$emit('refresh')"
          >
            <RefreshCw :class="cn('h-4 w-4', isFetching && 'animate-spin text-primary-600')" />
          </button>
        </Tooltip>
      </div>
    </div>

    <!-- Active filter chips -->
    <div v-if="filterChips?.length" class="flex flex-wrap items-center gap-1.5 px-2.5 pb-2.5 sm:px-3">
      <span
        v-for="chip in filterChips"
        :key="chip.id"
        class="inline-flex max-w-full items-center gap-1 rounded-full border border-border-default bg-subtle py-0.5 pl-2.5 pr-1 text-xs"
      >
        <span class="text-muted">{{ chip.label }}:</span>
        <span class="truncate font-medium text-primary">{{ chip.displayValue }}</span>
        <button
          type="button"
          class="rounded-full p-0.5 text-muted transition hover:bg-slate-200 hover:text-primary dark:hover:bg-slate-700"
          :aria-label="`Remove ${chip.label} filter`"
          @click="removeChip(chip)"
        >
          <X class="h-3 w-3" />
        </button>
      </span>
      <button
        type="button"
        class="ml-1 text-xs font-medium text-danger-600 hover:underline dark:text-danger-500"
        @click="$emit('clear-filters')"
      >
        Clear all
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import {
  Search, ListFilter, Bookmark, ChevronDown, Download, RefreshCw, X, Loader2, Check, Trash2,
  Rows2, Rows3, Rows4,
} from 'lucide-vue-next'
import DropdownMenu from '../ui/DropdownMenu.vue'
import Popover from '../ui/Popover.vue'
import Tooltip from '../ui/Tooltip.vue'
import Button from '../ui/Button.vue'
import Kbd from '../ui/Kbd.vue'
import DataTableColumnChooser from './DataTableColumnChooser.vue'
import { formatRelative } from '../../utils/format'
import { cn } from '../../utils/cn'

const props = defineProps({
  search: { type: String, default: '' },
  status: { type: String, default: 'all' },
  statusTabs: { type: Array, default: () => [] },
  counts: { type: Object, default: null },
  activeFiltersCount: { type: Number, default: 0 },
  filterChips: { type: Array, default: () => [] },
  allColumns: { type: Array, default: () => [] },
  hiddenColumns: { type: Array, default: () => [] },
  columnOrder: { type: Array, default: () => [] },
  hasCustomWidths: { type: Boolean, default: false },
  density: { type: String, default: 'normal' },
  isFetching: { type: Boolean, default: false },
  isExporting: { type: Boolean, default: false },
  lastUpdated: { type: Date, default: () => new Date() },
  savedViews: { type: Array, default: () => [] },
  activeViewId: { type: String, default: null },
  isViewModified: { type: Boolean, default: false },
})

const emit = defineEmits([
  'update:search', 'update:status', 'update:hiddenColumns', 'update:columnOrder', 'update:density',
  'open-filters', 'clear-filters', 'export', 'refresh', 'reset-columns', 'apply-view', 'save-view',
  'delete-view', 'filters-changed',
])

const toolBtn =
  'inline-flex h-9 shrink-0 items-center gap-1.5 rounded-lg border border-border-strong bg-surface px-3 text-[13px] font-medium text-secondary shadow-xs transition-colors hover:bg-subtle hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/40 data-[state=open]:bg-subtle data-[state=open]:text-primary'
const toolIconBtn =
  'inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border-strong bg-surface text-secondary shadow-xs transition-colors hover:bg-subtle hover:text-primary disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/40 data-[state=open]:bg-subtle'

// ----- Search (debounced, with local echo so typing never lags) -----
const searchRef = ref(null)
const localSearch = ref(props.search)
let searchTimer = null

watch(() => props.search, (v) => {
  if (v !== localSearch.value) localSearch.value = v
})

function onSearchInput(e) {
  localSearch.value = e.target.value
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => emit('update:search', localSearch.value.trim()), 300)
}

function clearSearch() {
  clearTimeout(searchTimer)
  localSearch.value = ''
  emit('update:search', '')
}

// "/" focuses search (unless already typing somewhere).
function onGlobalKey(e) {
  if (e.key !== '/' || e.metaKey || e.ctrlKey) return
  const t = e.target
  if (t instanceof HTMLElement && (t.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(t.tagName))) return
  e.preventDefault()
  searchRef.value?.focus()
}
onMounted(() => window.addEventListener('keydown', onGlobalKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onGlobalKey)
  clearTimeout(searchTimer)
})

// ----- Status counts -----
function countFor(value) {
  const c = props.counts || {}
  const n = c[value] ?? (value === 'all' ? c.all ?? c.total : undefined) ?? 0
  return Number(n).toLocaleString()
}

// ----- Chips -----
function removeChip(chip) {
  chip.onRemove()
  emit('filters-changed')
}

// ----- Density -----
const densityIcon = computed(() => ({ compact: Rows4, normal: Rows3, relaxed: Rows2 }[props.density] || Rows3))
const densityItems = computed(() => [
  { header: 'Row density' },
  ...[
    { key: 'compact', label: 'Compact', icon: Rows4 },
    { key: 'normal', label: 'Comfortable', icon: Rows3 },
    { key: 'relaxed', label: 'Spacious', icon: Rows2 },
  ].map((d) => ({
    label: d.label + (props.density === d.key ? '  ✓' : ''),
    icon: d.icon,
    action: () => emit('update:density', d.key),
  })),
])

// ----- Saved views -----
const viewsOpen = ref(false)
const newViewName = ref('')
const activeViewName = computed(() => props.savedViews.find((v) => v.id === props.activeViewId)?.name || null)
const relativeUpdated = computed(() => formatRelative(props.lastUpdated))

function applyView(v) {
  emit('apply-view', v)
  viewsOpen.value = false
}

function saveView() {
  const name = newViewName.value.trim()
  if (!name) return
  emit('save-view', name)
  newViewName.value = ''
  viewsOpen.value = false
}
</script>
