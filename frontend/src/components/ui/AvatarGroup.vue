<template>
  <div :class="cn('flex items-center -space-x-2 overflow-hidden', $attrs.class)">
    <slot />
    <span
      v-if="overflowCount > 0"
      :class="cn(
        'relative inline-flex items-center justify-center rounded-full bg-muted border border-border-default text-secondary text-[10px] font-semibold select-none ring-1 ring-surface',
        sizeClasses
      )"
    >
      +{{ overflowCount }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { cn } from '../../utils/cn'

const props = defineProps({
  overflowCount: {
    type: Number,
    default: 0,
  },
  size: {
    type: [Number, String],
    default: 32,
  },
})

const sizeClasses = computed(() => {
  const s = Number(props.size)
  return {
    20: 'w-5 h-5',
    24: 'w-6 h-6',
    32: 'w-8 h-8',
    40: 'w-10 h-10',
  }[s] || 'w-8 h-8'
})
</script>
