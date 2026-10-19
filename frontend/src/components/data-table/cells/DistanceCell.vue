<template>
  <span v-if="numericValue !== null" class="font-mono tabular-nums text-xs font-medium text-slate-800 dark:text-slate-200">
    {{ formattedDistance }}
  </span>
  <span v-else class="text-slate-400 dark:text-slate-600">—</span>
</template>

<script setup>
import { computed } from 'vue'
import { formatDistance } from '../../../utils/format'

const props = defineProps({
  value: [Number, String],
  row: Object,
  field: Object,
  name: String,
})

const numericValue = computed(() => {
  const v = props.value ?? props.row?.[props.name]
  if (v === null || v === undefined || v === '') return null
  const n = Number(v)
  return isNaN(n) ? null : n
})

const formattedDistance = computed(() => {
  if (numericValue.value === null) return '—'
  return formatDistance(numericValue.value)
})
</script>
