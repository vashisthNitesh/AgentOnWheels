<template>
  <div class="inline-flex items-center">
    <StatusPill v-if="status" :status="status" :label="label" size="sm" />
    <span v-else class="text-slate-400 dark:text-slate-600">—</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StatusPill from '../../ui/StatusPill.vue'

const props = defineProps({
  value: [String, Number],
  row: Object,
  field: Object,
  name: String,
})

const status = computed(() => props.value ?? props.row?.[props.name])
const label = computed(() => props.row?.[`${props.name}_label`] || undefined)
</script>
