<template>
  <span
    :class="cn(
      'inline-flex items-center gap-1.5 font-medium rounded-full border transition-colors select-none',
      sizeClasses,
      variantClasses,
      $attrs.class
    )"
  >
    <span v-if="dot" :class="cn('w-1.5 h-1.5 rounded-full shrink-0', dotClass)" />
    <slot />
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { cn } from '../../utils/cn'

const props = defineProps({
  variant: {
    type: String,
    default: 'neutral',
    validator: v => ['neutral', 'primary', 'success', 'warning', 'danger', 'info', 'accent'].includes(v),
  },
  size: {
    type: String,
    default: 'sm',
    validator: v => ['sm', 'md'].includes(v),
  },
  dot: {
    type: Boolean,
    default: false,
  },
})

const sizeClasses = computed(() => {
  return {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
  }[props.size]
})

const variantClasses = computed(() => {
  return {
    neutral: 'bg-subtle text-secondary border-border-default',
    primary: 'bg-primary-50 text-primary-700 border-primary-200 dark:bg-primary-950/40 dark:text-primary-300 dark:border-primary-800',
    accent: 'bg-accent-50 text-accent-700 border-accent-200 dark:bg-accent-950/40 dark:text-accent-300 dark:border-accent-800',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800',
    warning: 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800',
    danger: 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800',
    info: 'bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800',
  }[props.variant]
})

const dotClass = computed(() => {
  return {
    neutral: 'bg-slate-400',
    primary: 'bg-primary-500',
    accent: 'bg-accent-500',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-rose-500',
    info: 'bg-sky-500',
  }[props.variant]
})
</script>
