<template>
  <div v-if="numericValue !== null" class="inline-flex items-center">
    <Tooltip :content="kgTooltip">
      <span class="font-mono tabular-nums text-xs font-medium text-slate-800 dark:text-slate-200 cursor-default">
        {{ formattedTonnes }}
      </span>
    </Tooltip>
  </div>
  <span v-else class="text-slate-400 dark:text-slate-600">—</span>
</template>

<script setup>
import { computed } from 'vue'
import { formatNumber } from '../../../utils/format'
import Tooltip from '../../ui/Tooltip.vue'

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

const formattedTonnes = computed(() => {
  if (numericValue.value === null) return '—'
  return `${formatNumber(numericValue.value, 2)} t`
})

const kgTooltip = computed(() => {
  if (numericValue.value === null) return ''
  const kg = Math.round(numericValue.value * 1000)
  return `${formatNumber(kg, 0)} kg`
})
</script>
