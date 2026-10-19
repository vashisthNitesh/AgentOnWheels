<template>
  <div class="inline-flex items-center">
    <span
      v-if="isTrue"
      class="inline-flex items-center justify-center h-5 w-5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 font-bold text-xs"
      title="Yes"
    >
      ✓
    </span>
    <span v-else class="text-slate-400 dark:text-slate-600">—</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: [Boolean, String, Number],
  row: Object,
  field: Object,
  name: String,
})

const isTrue = computed(() => {
  const v = props.value ?? props.row?.[props.name]
  return v === true || v === 'true' || v === 1
})
</script>
