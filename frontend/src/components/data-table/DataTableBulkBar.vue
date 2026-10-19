<template>
  <Transition
    enter-active-class="transform transition ease-out duration-200"
    enter-from-class="translate-y-12 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transform transition ease-in duration-150"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-12 opacity-0"
  >
    <div
      v-if="selectedCount > 0"
      class="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 max-w-2xl w-auto px-4 py-2.5 rounded-xl border border-slate-700/80 bg-slate-900/95 dark:bg-slate-900/95 text-white shadow-2xl backdrop-blur-md flex items-center gap-3 sm:gap-4 select-none"
    >
      <!-- Selected count & select all matching button -->
      <div class="flex items-center gap-2 pr-2 border-r border-slate-700 text-xs sm:text-sm">
        <span class="inline-flex items-center justify-center h-5 px-2 rounded-full bg-brand-500 font-bold text-[11px] text-white">
          {{ isAllMatching ? totalCount : selectedCount }}
        </span>
        <span class="font-medium text-slate-200">
          {{ isAllMatching ? 'All' : '' }} selected
        </span>

        <button
          v-if="!isAllMatching && totalCount > selectedCount"
          type="button"
          class="ml-1 text-xs text-brand-400 hover:text-brand-300 underline font-medium cursor-pointer"
          @click="$emit('select-all-matching')"
        >
          Select all {{ totalCount }} matching
        </button>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white transition-colors cursor-pointer border border-slate-700"
          @click="$emit('export-selected')"
        >
          <Download class="w-3.5 h-3.5" />
          <span>Export</span>
        </button>

        <slot name="actions" />

        <button
          v-if="allowDelete"
          type="button"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-lg bg-rose-950/60 hover:bg-rose-900/80 text-rose-300 hover:text-rose-100 transition-colors cursor-pointer border border-rose-800/50"
          @click="$emit('delete-selected')"
        >
          <Trash2 class="w-3.5 h-3.5" />
          <span>Delete</span>
        </button>
      </div>

      <!-- Clear selection button -->
      <button
        type="button"
        class="inline-flex items-center justify-center h-6 w-6 rounded-full hover:bg-slate-800 text-slate-400 hover:text-white transition-colors cursor-pointer ml-1"
        title="Deselect all (Esc)"
        @click="$emit('clear')"
      >
        <X class="w-4 h-4" />
      </button>
    </div>
  </Transition>
</template>

<script setup>
import { Download, Trash2, X } from 'lucide-vue-next'

defineProps({
  selectedCount: {
    type: Number,
    required: true,
  },
  totalCount: {
    type: Number,
    default: 0,
  },
  isAllMatching: {
    type: Boolean,
    default: false,
  },
  allowDelete: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['clear', 'select-all-matching', 'export-selected', 'delete-selected'])
</script>
