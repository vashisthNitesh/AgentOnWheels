<template>
  <div v-if="dateValue" class="inline-flex items-center">
    <Tooltip :content="relativeTime">
      <span class="font-mono text-xs tabular-nums text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors cursor-default">
        {{ formattedDate }}
      </span>
    </Tooltip>
  </div>
  <span v-else class="text-slate-400 dark:text-slate-600">—</span>
</template>

<script setup>
import { computed } from 'vue'
import { formatDate, formatDateTime, formatRelative } from '../../../utils/format'
import Tooltip from '../../ui/Tooltip.vue'

const props = defineProps({
  value: [String, Date],
  row: Object,
  field: Object,
  name: String,
  includeTime: Boolean,
})

const dateValue = computed(() => props.value ?? props.row?.[props.name])

const isDateTime = computed(() => {
  if (props.includeTime) return true
  if (props.field?.type === 'datetime') return true
  if (typeof dateValue.value === 'string' && (dateValue.value.includes('T') || dateValue.value.includes(':'))) {
    return true
  }
  return false
})

const formattedDate = computed(() => {
  if (!dateValue.value) return '—'
  return isDateTime.value ? formatDateTime(dateValue.value) : formatDate(dateValue.value)
})

const relativeTime = computed(() => {
  if (!dateValue.value) return ''
  return formatRelative(dateValue.value)
})
</script>
