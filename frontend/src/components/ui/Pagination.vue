<template>
  <div
    :class="cn(
      'flex flex-col sm:flex-row items-center justify-between gap-3 px-4 py-3 border-t border-border-default bg-surface text-xs text-secondary select-none',
      $attrs.class
    )"
  >
    <!-- Left: Page Size Selector & Showing Counter -->
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-1.5">
        <span>Rows per page</span>
        <select
          :value="pageSize"
          class="h-7 rounded border border-border-strong bg-surface px-2 text-xs text-primary focus-ring cursor-pointer"
          @change="onPageSizeChange"
        >
          <option v-for="s in pageSizes" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>

      <span class="text-muted hidden sm:inline">|</span>

      <span class="tabular-nums font-medium text-primary">
        {{ rangeText }}
      </span>
    </div>

    <!-- Right: Page Navigation -->
    <div class="flex items-center gap-1">
      <!-- First Page Button -->
      <button
        type="button"
        :disabled="page <= 1"
        class="h-7 w-7 rounded border border-border-default bg-surface hover:bg-subtle flex items-center justify-center transition disabled:opacity-40 disabled:pointer-events-none focus-ring"
        title="First page"
        aria-label="First page"
        @click="goTo(1)"
      >
        <ChevronsLeft class="w-3.5 h-3.5" />
      </button>

      <!-- Previous Page Button -->
      <button
        type="button"
        :disabled="page <= 1"
        class="h-7 w-7 rounded border border-border-default bg-surface hover:bg-subtle flex items-center justify-center transition disabled:opacity-40 disabled:pointer-events-none focus-ring"
        title="Previous page"
        aria-label="Previous page"
        @click="goTo(page - 1)"
      >
        <ChevronLeft class="w-3.5 h-3.5" />
      </button>

      <!-- Page Numbers with Ellipsis -->
      <template v-for="(p, idx) in visiblePages" :key="idx">
        <span v-if="p === '...'" class="px-1 text-muted select-none">…</span>
        <button
          v-else
          type="button"
          :class="cn(
            'h-7 min-w-[28px] px-1.5 rounded text-xs font-medium tabular-nums transition focus-ring',
            p === page
              ? 'bg-primary-600 text-white font-semibold dark:bg-primary-500 shadow-xs'
              : 'border border-border-default bg-surface text-secondary hover:text-primary hover:bg-subtle'
          )"
          @click="goTo(p)"
        >
          {{ p }}
        </button>
      </template>

      <!-- Next Page Button -->
      <button
        type="button"
        :disabled="page >= totalPages"
        class="h-7 w-7 rounded border border-border-default bg-surface hover:bg-subtle flex items-center justify-center transition disabled:opacity-40 disabled:pointer-events-none focus-ring"
        title="Next page"
        aria-label="Next page"
        @click="goTo(page + 1)"
      >
        <ChevronRight class="w-3.5 h-3.5" />
      </button>

      <!-- Last Page Button -->
      <button
        type="button"
        :disabled="page >= totalPages"
        class="h-7 w-7 rounded border border-border-default bg-surface hover:bg-subtle flex items-center justify-center transition disabled:opacity-40 disabled:pointer-events-none focus-ring"
        title="Last page"
        aria-label="Last page"
        @click="goTo(totalPages)"
      >
        <ChevronsRight class="w-3.5 h-3.5" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from 'lucide-vue-next'
import { cn } from '../../utils/cn'

const props = defineProps({
  page: {
    type: Number,
    default: 1,
  },
  pageSize: {
    type: Number,
    default: 20,
  },
  total: {
    type: Number,
    default: 0,
  },
  pageSizes: {
    type: Array,
    default: () => [20, 50, 100],
  },
})

const emit = defineEmits(['update:page', 'update:pageSize', 'change'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

const rangeText = computed(() => {
  if (props.total === 0) return '0 records'
  const start = (props.page - 1) * props.pageSize + 1
  const end = Math.min(props.page * props.pageSize, props.total)
  return `Showing ${start.toLocaleString()}–${end.toLocaleString()} of ${props.total.toLocaleString()}`
})

const visiblePages = computed(() => {
  const current = props.page
  const total = totalPages.value
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const pages = []
  pages.push(1)

  if (current > 3) {
    pages.push('...')
  }

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  if (current < total - 2) {
    pages.push('...')
  }

  pages.push(total)
  return pages
})

function goTo(p) {
  if (p < 1 || p > totalPages.value || p === props.page) return
  emit('update:page', p)
  emit('change', { page: p, pageSize: props.pageSize })
}

function onPageSizeChange(e) {
  const newSize = Number(e.target.value)
  emit('update:pageSize', newSize)
  emit('update:page', 1)
  emit('change', { page: 1, pageSize: newSize })
}
</script>
