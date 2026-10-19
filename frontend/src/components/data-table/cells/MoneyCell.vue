<template>
  <span :class="['font-mono tabular-nums text-right block', textClass]">
    {{ formatted }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { formatCurrency } from '../../../utils/format'

const props = defineProps({
  value: [Number, String],
  row: Object,
  field: Object,
  name: String,
})

const rawValue = computed(() => props.value ?? props.row?.[props.name])
const currency = computed(() => props.row?.currency || 'AED')

const formatted = computed(() => {
  return formatCurrency(rawValue.value, currency.value)
})

const textClass = computed(() => {
  if (rawValue.value === null || rawValue.value === undefined || rawValue.value === '') {
    return 'text-slate-400 dark:text-slate-600'
  }
  return 'text-slate-900 dark:text-slate-100 font-medium'
})
</script>
