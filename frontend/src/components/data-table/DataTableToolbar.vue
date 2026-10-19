<template>
  <div class="space-y-3">
    <!-- Status Tabs (if status field exists) -->
    <div
      v-if="statusTabs?.length > 1"
      class="flex items-center gap-1 overflow-x-auto pb-1 scrollbar-none border-b border-slate-200 dark:border-slate-800"
    >
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        type="button"
        :class="[
          'relative px-3.5 py-1.5 text-xs font-semibold rounded-md transition-all flex items-center gap-2 whitespace-nowrap cursor-pointer select-none',
          status === tab.value
            ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-xs'
            : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/60'
        ]"
        @click="$emit('update:status', tab.value)"
      >
        <span>{{ tab.label }}</span>
        <span
          v-if="counts"
          :class="[
            'px-1.5 py-0.2 rounded-full text-[10px] font-mono tabular-nums transition-colors',
            status === tab.value
              ? 'bg-white/20 text-white dark:bg-black/20 dark:text-slate-900'
              : 'bg-slate-200/70 text-slate-700 dark:bg-slate-800 dark:text-slate-400'
          ]"
        >
          {{ counts[tab.value] ?? (tab.value === 'all' ? (counts.all ?? counts.total ?? 0) : 0) }}
        </span>
      </button>
    </div>

    <!-- Main Toolbar Row -->
    <div class="flex flex-wrap items-center justify-between gap-2.5">
      <!-- Left side: Search & Filters -->
      <div class="flex flex-wrap items-center gap-2 flex-1 min-w-[280px]">
        <!-- Search Input with Debounce & Spinner -->
        <div class="relative w-full max-w-xs">
          <Search class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input
            :value="search"
            type="text"
            placeholder="Search records… (Esc to clear)"
            class="w-full pl-8 pr-8 py-1.5 text-xs rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 shadow-xs focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
            @input="onSearchInput"
            @keydown.esc="$emit('update:search', '')"
          />
          <span v-if="isFetching" class="absolute right-2.5 top-2.5">
            <Loader2 class="h-3.5 w-3.5 animate-spin text-brand-600" />
          </span>
          <button
            v-else-if="search"
            type="button"
            class="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            @click="$emit('update:search', '')"
          >
            <X class="h-3.5 w-3.5" />
          </button>
        </div>

        <!-- Filter Drawer Trigger Button -->
        <button
          type="button"
          :class="[
            'inline-flex items-center gap-1.5 h-8 px-2.5 text-xs font-medium rounded-md border transition-colors shadow-xs cursor-pointer',
            activeFiltersCount > 0
              ? 'border-brand-500/40 bg-brand-50/50 dark:bg-brand-950/30 text-brand-700 dark:text-brand-300'
              : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
          ]"
          @click="$emit('open-filters')"
        >
          <Filter class="w-3.5 h-3.5" />
          <span>Filters</span>
          <span
            v-if="activeFiltersCount > 0"
            class="ml-0.5 px-1.5 py-0.2 rounded-full text-[10px] font-semibold bg-brand-600 text-white"
          >
            {{ activeFiltersCount }}
          </span>
        </button>

        <!-- Saved Views Dropdown -->
        <DropdownMenu :items="viewsMenuItems" align="start">
          <template #trigger>
            <button
              type="button"
              class="inline-flex items-center gap-1.5 h-8 px-2.5 text-xs font-medium rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-xs cursor-pointer"
              title="Saved Views"
            >
              <Bookmark class="w-3.5 h-3.5 text-slate-500" />
              <span>{{ activeViewName || 'Views' }}</span>
              <span
                v-if="isViewModified"
                class="w-1.5 h-1.5 rounded-full bg-amber-500"
                title="View has unsaved changes"
              />
              <ChevronDown class="w-3 h-3 text-slate-400" />
            </button>
          </template>
        </DropdownMenu>
      </div>

      <!-- Right side: Columns, Density, Export, Refresh -->
      <div class="flex items-center gap-1.5">
        <!-- Columns Chooser -->
        <DataTableColumnChooser
          :columns="allColumns"
          :hidden-columns="hiddenColumns"
          :column-order="columnOrder"
          @update:hidden-columns="$emit('update:hiddenColumns', $event)"
          @update:column-order="$emit('update:columnOrder', $event)"
          @reset="$emit('reset-columns')"
        />

        <!-- Density Toggle -->
        <DropdownMenu
          :items="[
            { label: 'Compact', action: () => $emit('update:density', 'compact') },
            { label: 'Normal', action: () => $emit('update:density', 'normal') },
            { label: 'Relaxed', action: () => $emit('update:density', 'relaxed') },
          ]"
          align="end"
        >
          <template #trigger>
            <button
              type="button"
              class="inline-flex items-center justify-center h-8 w-8 text-xs font-medium rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-xs"
              title="Row density"
            >
              <Rows3 class="w-3.5 h-3.5 text-slate-500" />
            </button>
          </template>
        </DropdownMenu>

        <!-- CSV Export Button -->
        <button
          type="button"
          :disabled="isExporting"
          class="inline-flex items-center gap-1.5 h-8 px-2.5 text-xs font-medium rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-xs disabled:opacity-50 cursor-pointer"
          title="Export as CSV"
          @click="$emit('export')"
        >
          <Loader2 v-if="isExporting" class="w-3.5 h-3.5 animate-spin text-brand-600" />
          <Download v-else class="w-3.5 h-3.5 text-slate-500" />
          <span class="hidden sm:inline">{{ isExporting ? 'Exporting…' : 'Export' }}</span>
        </button>

        <!-- Refresh Button with Tooltip -->
        <Tooltip :content="`Last updated ${relativeUpdated}`">
          <button
            type="button"
            :disabled="isFetching"
            class="inline-flex items-center justify-center h-8 w-8 text-xs font-medium rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-xs disabled:opacity-50 cursor-pointer"
            @click="$emit('refresh')"
          >
            <RefreshCw :class="['w-3.5 h-3.5 text-slate-500', isFetching && 'animate-spin text-brand-600']" />
          </button>
        </Tooltip>
      </div>
    </div>

    <!-- Active Filter Chips Bar -->
    <div v-if="filterChips?.length > 0" class="flex flex-wrap items-center gap-1.5 pt-0.5">
      <span class="text-xs text-slate-400 dark:text-slate-500 mr-1 font-medium">Active:</span>
      <span
        v-for="chip in filterChips"
        :key="chip.id"
        class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 group transition-colors"
      >
        <span class="font-normal text-slate-500 dark:text-slate-400">{{ chip.label }}:</span>
        <span class="font-semibold">{{ chip.displayValue }}</span>
        <button
          type="button"
          class="text-slate-400 hover:text-slate-700 dark:hover:text-white rounded-full p-0.5"
          @click="chip.onRemove"
        >
          <X class="w-3 h-3" />
        </button>
      </span>

      <button
        type="button"
        class="text-xs font-medium text-rose-600 dark:text-rose-400 hover:underline ml-1 cursor-pointer"
        @click="$emit('clear-filters')"
      >
        Clear all
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Search,
  Filter,
  Bookmark,
  ChevronDown,
  Rows3,
  Download,
  RefreshCw,
  X,
  Loader2,
  Check,
} from 'lucide-vue-next'
import DropdownMenu from '../ui/DropdownMenu.vue'
import Tooltip from '../ui/Tooltip.vue'
import DataTableColumnChooser from './DataTableColumnChooser.vue'
import { formatRelative } from '../../utils/format'

const props = defineProps({
  search: {
    type: String,
    default: '',
  },
  status: {
    type: String,
    default: 'all',
  },
  statusTabs: {
    type: Array,
    default: () => [],
  },
  counts: {
    type: Object,
    default: null,
  },
  activeFiltersCount: {
    type: Number,
    default: 0,
  },
  filterChips: {
    type: Array,
    default: () => [],
  },
  allColumns: {
    type: Array,
    default: () => [],
  },
  hiddenColumns: {
    type: Array,
    default: () => [],
  },
  columnOrder: {
    type: Array,
    default: () => [],
  },
  density: {
    type: String,
    default: 'normal',
  },
  isFetching: {
    type: Boolean,
    default: false,
  },
  isExporting: {
    type: Boolean,
    default: false,
  },
  lastUpdated: {
    type: Date,
    default: () => new Date(),
  },
  savedViews: {
    type: Array,
    default: () => [],
  },
  activeViewId: {
    type: String,
    default: null,
  },
  isViewModified: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'update:search',
  'update:status',
  'update:hiddenColumns',
  'update:columnOrder',
  'update:density',
  'open-filters',
  'clear-filters',
  'export',
  'refresh',
  'reset-columns',
  'apply-view',
  'save-view',
  'delete-view',
])

let searchDebounceTimer = null
function onSearchInput(e) {
  const val = e.target.value
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    emit('update:search', val)
  }, 300)
}

const relativeUpdated = computed(() => {
  return formatRelative(props.lastUpdated)
})

const activeViewName = computed(() => {
  const v = props.savedViews.find((view) => view.id === props.activeViewId)
  return v?.name || null
})

const viewsMenuItems = computed(() => {
  const items = []

  if (props.savedViews.length > 0) {
    items.push({ header: 'Saved Views' })
    props.savedViews.forEach((v) => {
      items.push({
        label: v.name,
        icon: v.id === props.activeViewId ? Check : null,
        action: () => emit('apply-view', v),
      })
    })
    items.push({ separator: true })
  }

  items.push({
    label: 'Save current view as…',
    action: () => {
      const name = prompt('Enter a name for this view:')
      if (name && name.trim()) {
        emit('save-view', name.trim())
      }
    },
  })

  if (props.activeViewId) {
    items.push({
      label: 'Delete active view',
      danger: true,
      action: () => emit('delete-view', props.activeViewId),
    })
  }

  return items
})
</script>
