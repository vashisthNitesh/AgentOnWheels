<template>
  <router-link
    v-if="to && displayValue !== '—'"
    :to="to"
    class="font-medium text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 hover:underline inline-flex items-center gap-1 group/link max-w-full truncate"
    @click.stop
  >
    <span class="truncate">{{ displayValue }}</span>
  </router-link>
  <span v-else :class="displayValue === '—' ? 'text-slate-400 dark:text-slate-600' : 'text-slate-900 dark:text-slate-100'">
    {{ displayValue }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: [String, Number],
  row: Object,
  field: Object,
  name: String,
  to: [String, Object],
})

const displayValue = computed(() => {
  if (props.row?.[`${props.name}_label`] !== undefined) {
    const l = props.row[`${props.name}_label`]
    return Array.isArray(l) ? l.join(', ') : (l || '—')
  }
  const v = props.value ?? props.row?.[props.name]
  if (v === null || v === undefined || v === '') return '—'
  return String(v)
})
</script>
