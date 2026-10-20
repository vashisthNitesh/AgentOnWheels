<template>
  <nav
    aria-label="Pagination"
    :class="cn(
      'flex flex-wrap items-center justify-between gap-x-4 gap-y-2 px-3 py-2 text-xs text-secondary select-none sm:px-4',
      $attrs.class
    )"
  >
    <!-- Left: rows per page + range -->
    <div class="flex min-w-0 items-center gap-3">
      <label class="hidden items-center gap-2 sm:flex">
        <span class="whitespace-nowrap text-muted">Rows per page</span>
        <Select
          :model-value="pageSize"
          :options="pageSizeOptions"
          size="sm"
          class="w-[72px]"
          aria-label="Rows per page"
          @update:model-value="onPageSizeChange"
        />
      </label>

      <span class="hidden h-4 w-px bg-border-default sm:block" aria-hidden="true" />

      <span class="whitespace-nowrap tabular-nums" aria-live="polite">
        <template v-if="total === 0">No records</template>
        <template v-else>
          <span class="font-semibold text-primary">{{ start.toLocaleString() }}–{{ end.toLocaleString() }}</span>
          <span class="text-muted"> of </span>
          <span class="font-semibold text-primary">{{ total.toLocaleString() }}</span>
        </template>
      </span>
    </div>

    <!-- Right: navigation -->
    <div class="flex items-center gap-1">
      <button
        type="button"
        class="pg-btn hidden sm:inline-flex"
        :disabled="page <= 1"
        aria-label="First page"
        title="First page"
        @click="goTo(1)"
      >
        <ChevronsLeft class="h-4 w-4" />
      </button>
      <button
        type="button"
        class="pg-btn"
        :disabled="page <= 1"
        aria-label="Previous page"
        title="Previous page"
        @click="goTo(page - 1)"
      >
        <ChevronLeft class="h-4 w-4" />
      </button>

      <!-- Desktop: numbered pages -->
      <div class="hidden items-center gap-1 md:flex">
        <template v-for="(p, idx) in visiblePages" :key="`${p}-${idx}`">
          <span v-if="p === '…'" class="w-7 text-center text-muted">…</span>
          <button
            v-else
            type="button"
            :aria-current="p === page ? 'page' : undefined"
            :class="cn(
              'h-8 min-w-[2rem] rounded-md px-2 text-xs font-medium tabular-nums transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/50',
              p === page
                ? 'bg-primary-600 text-white shadow-xs dark:bg-primary-500'
                : 'text-secondary hover:bg-subtle hover:text-primary'
            )"
            @click="goTo(p)"
          >
            {{ p }}
          </button>
        </template>
      </div>

      <!-- Mobile / compact: page x of y -->
      <span class="px-2 tabular-nums md:hidden">
        <span class="font-semibold text-primary">{{ page }}</span>
        <span class="text-muted"> / {{ totalPages }}</span>
      </span>

      <button
        type="button"
        class="pg-btn"
        :disabled="page >= totalPages"
        aria-label="Next page"
        title="Next page"
        @click="goTo(page + 1)"
      >
        <ChevronRight class="h-4 w-4" />
      </button>
      <button
        type="button"
        class="pg-btn hidden sm:inline-flex"
        :disabled="page >= totalPages"
        aria-label="Last page"
        title="Last page"
        @click="goTo(totalPages)"
      >
        <ChevronsRight class="h-4 w-4" />
      </button>

      <!-- Jump to page -->
      <form
        v-if="totalPages > 7"
        class="ml-2 hidden items-center gap-1.5 lg:flex"
        @submit.prevent="jump"
      >
        <span class="text-muted">Go to</span>
        <input
          v-model="jumpValue"
          type="number"
          min="1"
          :max="totalPages"
          inputmode="numeric"
          :placeholder="String(page)"
          aria-label="Go to page"
          class="h-8 w-14 rounded-md border border-border-strong bg-surface px-2 text-center text-xs tabular-nums text-primary outline-none transition [appearance:textfield] focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15 [&::-webkit-inner-spin-button]:appearance-none"
          @blur="jump"
        />
      </form>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-vue-next'
import { cn } from '../../utils/cn'
import Select from './Select.vue'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  total: { type: Number, default: 0 },
  pageSizes: { type: Array, default: () => [10, 20, 50, 100] },
})

const emit = defineEmits(['update:page', 'update:pageSize', 'change'])

const jumpValue = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
const start = computed(() => (props.total === 0 ? 0 : (props.page - 1) * props.pageSize + 1))
const end = computed(() => Math.min(props.page * props.pageSize, props.total))

const pageSizeOptions = computed(() => {
  const sizes = new Set([...props.pageSizes, props.pageSize])
  return [...sizes].sort((a, b) => a - b).map((s) => ({ value: s, label: String(s) }))
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = Math.min(props.page, total)
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  // Always show 7 slots so the control never changes width while paging.
  if (current <= 4) return [1, 2, 3, 4, 5, '…', total]
  if (current >= total - 3) return [1, '…', total - 4, total - 3, total - 2, total - 1, total]
  return [1, '…', current - 1, current, current + 1, '…', total]
})

function goTo(p) {
  const target = Math.min(Math.max(1, p), totalPages.value)
  if (target === props.page) return
  emit('update:page', target)
  emit('change', { page: target, pageSize: props.pageSize })
}

function jump() {
  const n = parseInt(jumpValue.value, 10)
  jumpValue.value = ''
  if (!Number.isNaN(n)) goTo(n)
}

function onPageSizeChange(val) {
  const size = Number(val)
  if (!size || size === props.pageSize) return
  emit('update:pageSize', size)
  emit('change', { page: 1, pageSize: size })
}
</script>

<style scoped>
.pg-btn {
  @apply inline-flex h-8 w-8 items-center justify-center rounded-md text-secondary transition-colors hover:bg-subtle hover:text-primary disabled:pointer-events-none disabled:opacity-35 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/50;
}
</style>
