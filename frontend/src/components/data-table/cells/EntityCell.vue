<template>
  <div class="inline-flex items-center gap-2 max-w-full">
    <Avatar
      v-if="displayName && displayName !== '—'"
      :name="displayName"
      size="sm"
      class="flex-shrink-0"
    />
    <div class="min-w-0 flex-1">
      <span class="block truncate font-medium text-slate-900 dark:text-slate-100 text-sm">
        {{ displayName }}
      </span>
      <span v-if="subText" class="block truncate text-xs text-slate-500 dark:text-slate-400">
        {{ subText }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Avatar from '../../ui/Avatar.vue'

const props = defineProps({
  value: [String, Object, Number],
  row: Object,
  field: Object,
  name: String,
  subtitleField: String,
})

const displayName = computed(() => {
  if (props.row?.[`${props.name}_label`] !== undefined) {
    const l = props.row[`${props.name}_label`]
    return Array.isArray(l) ? l.join(', ') : (l || '—')
  }
  const v = props.value ?? props.row?.[props.name]
  if (v === null || v === undefined || v === '') return '—'
  return String(v)
})

const subText = computed(() => {
  if (!props.subtitleField) return ''
  return props.row?.[props.subtitleField] || ''
})
</script>
