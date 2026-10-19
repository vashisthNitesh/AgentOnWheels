<template>
  <!-- Card Skeleton -->
  <div
    v-if="variant === 'card'"
    :class="cn('rounded-lg border border-border-default bg-surface p-5 space-y-4 animate-pulse', $attrs.class)"
  >
    <div class="h-4 w-1/3 bg-muted rounded" />
    <div class="h-8 w-1/2 bg-muted rounded" />
    <div class="space-y-2 pt-2">
      <div class="h-3 w-full bg-muted rounded" />
      <div class="h-3 w-4/5 bg-muted rounded" />
    </div>
  </div>

  <!-- Table Rows Skeleton -->
  <tbody v-else-if="variant === 'table-rows'" :class="$attrs.class">
    <tr v-for="n in count" :key="n" class="border-b border-border-default">
      <td v-for="col in columns" :key="col" class="py-3 px-4">
        <div class="h-3.5 bg-muted rounded animate-pulse w-full max-w-[120px]" />
      </td>
    </tr>
  </tbody>

  <!-- Avatar Skeleton -->
  <div
    v-else-if="variant === 'avatar'"
    :class="cn('rounded-full bg-muted animate-pulse shrink-0', sizeClasses, $attrs.class)"
  />

  <!-- Chart Skeleton -->
  <div
    v-else-if="variant === 'chart'"
    :class="cn('rounded-lg border border-border-default bg-surface p-5 animate-pulse space-y-4 flex flex-col justify-between', $attrs.class)"
  >
    <div class="h-4 w-1/4 bg-muted rounded" />
    <div class="flex items-end gap-3 h-48 pt-6">
      <div v-for="n in 8" :key="n" class="flex-1 bg-muted rounded-t" :style="{ height: `${20 + (n * 9) % 80}%` }" />
    </div>
  </div>

  <!-- Standard Text Line Skeleton (Default) -->
  <div
    v-else
    :class="cn('bg-muted rounded animate-pulse', heightClasses, widthClass, $attrs.class)"
  />
</template>

<script setup>
import { computed } from 'vue'
import { cn } from '../../utils/cn'

const props = defineProps({
  variant: {
    type: String,
    default: 'text',
    validator: v => ['text', 'card', 'table-rows', 'avatar', 'chart'].includes(v),
  },
  count: {
    type: Number,
    default: 5,
  },
  columns: {
    type: Number,
    default: 6,
  },
  size: {
    type: [String, Number],
    default: 'md',
  },
  width: {
    type: String,
    default: 'w-full',
  },
})

const sizeClasses = computed(() => {
  return {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10',
  }[props.size] || 'w-8 h-8'
})

const heightClasses = computed(() => {
  return {
    sm: 'h-2.5',
    md: 'h-3.5',
    lg: 'h-5',
  }[props.size] || 'h-3.5'
})

const widthClass = computed(() => props.width)
</script>
