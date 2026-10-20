<template>
  <!-- Floats just above the pagination footer, inside the table card. -->
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="translate-y-3 opacity-0"
    leave-active-class="transition duration-150 ease-in"
    leave-to-class="translate-y-3 opacity-0"
  >
    <div
      v-if="selectedCount > 0"
      class="pointer-events-none absolute inset-x-0 bottom-16 z-40 flex justify-center px-3"
    >
      <div
        role="toolbar"
        aria-label="Bulk actions"
        class="pointer-events-auto flex max-w-full items-center gap-1 overflow-x-auto rounded-xl border border-slate-700 bg-slate-900 py-1.5 pl-3 pr-1.5 text-white shadow-xl shadow-slate-900/30 dark:border-slate-600 dark:bg-slate-800"
      >
        <span class="flex shrink-0 items-center gap-2 pr-2 text-[13px]">
          <span class="rounded-md bg-primary-500 px-1.5 text-xs font-bold tabular-nums leading-5">
            {{ (isAllMatching ? totalCount : selectedCount).toLocaleString() }}
          </span>
          <span class="font-medium text-slate-200">{{ isAllMatching ? 'all matching' : 'selected' }}</span>
        </span>

        <button
          v-if="!isAllMatching && totalCount > selectedCount"
          type="button"
          class="shrink-0 rounded-md px-2 py-1 text-xs font-medium text-primary-300 transition hover:bg-white/10 hover:text-primary-200"
          @click="$emit('select-all-matching')"
        >
          Select all {{ totalCount.toLocaleString() }}
        </button>

        <span class="mx-1 h-5 w-px shrink-0 bg-white/15" />

        <button type="button" class="bulk-btn" @click="$emit('export-selected')">
          <Download class="h-3.5 w-3.5" />
          Export
        </button>

        <slot name="actions" />

        <button
          v-if="allowDelete"
          type="button"
          class="inline-flex h-7 shrink-0 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-rose-300 transition hover:bg-rose-500/20 hover:text-rose-200"
          @click="$emit('delete-selected')"
        >
          <Trash2 class="h-3.5 w-3.5" />
          Delete
        </button>

        <span class="mx-1 h-5 w-px shrink-0 bg-white/15" />

        <button
          type="button"
          class="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-slate-400 transition hover:bg-white/10 hover:text-white"
          title="Clear selection (Esc)"
          aria-label="Clear selection"
          @click="$emit('clear')"
        >
          <X class="h-4 w-4" />
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { Download, Trash2, X } from 'lucide-vue-next'

const props = defineProps({
  selectedCount: { type: Number, required: true },
  totalCount: { type: Number, default: 0 },
  isAllMatching: { type: Boolean, default: false },
  allowDelete: { type: Boolean, default: false },
})

const emit = defineEmits(['clear', 'select-all-matching', 'export-selected', 'delete-selected'])

function onKey(e) {
  if (e.key !== 'Escape' || props.selectedCount === 0) return
  // Don't hijack Esc while a dialog, menu or input is handling it.
  if (document.querySelector('[role="dialog"], [role="menu"], [role="listbox"]')) return
  if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return
  emit('clear')
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<style scoped>
.bulk-btn {
  @apply inline-flex h-7 shrink-0 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-slate-200 transition hover:bg-white/10 hover:text-white;
}
</style>
