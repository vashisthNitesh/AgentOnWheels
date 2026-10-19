<template>
  <div class="group inline-flex items-center gap-1.5 font-mono text-xs font-semibold text-slate-800 dark:text-slate-200">
    <span class="tracking-tight">{{ displayVal }}</span>
    <CopyButton
      v-if="displayVal !== '—'"
      :text="String(displayVal)"
      class="opacity-0 group-hover:opacity-100 transition-opacity !h-5 !w-5"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CopyButton from '../../ui/CopyButton.vue'

const props = defineProps({
  value: [String, Number],
  row: Object,
  field: Object,
  name: String,
})

const displayVal = computed(() => {
  const v = props.value ?? props.row?.[props.name]
  if (v === null || v === undefined || v === '') return '—'
  return v
})
</script>
