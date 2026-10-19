<template>
  <div v-if="items.length" class="flex flex-wrap items-center gap-1 max-w-full">
    <Badge
      v-for="(item, idx) in visibleItems"
      :key="idx"
      variant="secondary"
      size="sm"
      class="max-w-[120px] truncate"
    >
      {{ item }}
    </Badge>
    <Badge
      v-if="remainingCount > 0"
      variant="outline"
      size="sm"
      :title="items.slice(maxVisible).join(', ')"
    >
      +{{ remainingCount }}
    </Badge>
  </div>
  <span v-else class="text-slate-400 dark:text-slate-600">—</span>
</template>

<script setup>
import { computed } from 'vue'
import Badge from '../../ui/Badge.vue'

const props = defineProps({
  value: [Array, String],
  row: Object,
  field: Object,
  name: String,
  maxVisible: {
    type: Number,
    default: 2,
  },
})

const items = computed(() => {
  const v = props.value ?? props.row?.[`${props.name}_label`] ?? props.row?.[props.name]
  if (!v) return []
  if (Array.isArray(v)) return v
  if (typeof v === 'string') return v.split(',').map((s) => s.trim()).filter(Boolean)
  return [String(v)]
})

const visibleItems = computed(() => items.value.slice(0, props.maxVisible))
const remainingCount = computed(() => Math.max(0, items.value.length - props.maxVisible))
</script>
