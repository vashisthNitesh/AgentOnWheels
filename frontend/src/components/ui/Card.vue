<template>
  <div
    :class="cn(
      'rounded-lg border border-border-default bg-surface shadow-xs transition-colors',
      $attrs.class
    )"
  >
    <!-- Card Header -->
    <div
      v-if="$slots.header || title || $slots.title || $slots.actions"
      :class="cn(
        'flex items-center justify-between gap-4 border-b border-border-default',
        paddingClasses
      )"
    >
      <slot name="header">
        <div>
          <h3 v-if="title || $slots.title" class="text-sm font-semibold text-primary">
            <slot name="title">{{ title }}</slot>
          </h3>
          <p v-if="subtitle || $slots.subtitle" class="text-xs text-secondary mt-0.5">
            <slot name="subtitle">{{ subtitle }}</slot>
          </p>
        </div>
        <div v-if="$slots.actions" class="flex items-center gap-2 ml-auto">
          <slot name="actions" />
        </div>
      </slot>
    </div>

    <!-- Card Body -->
    <div :class="[padding !== 'none' && paddingClasses, bodyClass]">
      <slot />
    </div>

    <!-- Card Footer -->
    <div
      v-if="$slots.footer"
      :class="cn(
        'border-t border-border-default bg-subtle/50 rounded-b-lg flex items-center justify-between gap-3',
        paddingClasses
      )"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { cn } from '../../utils/cn'

const props = defineProps({
  title: {
    type: String,
    default: '',
  },
  subtitle: {
    type: String,
    default: '',
  },
  padding: {
    type: String,
    default: 'md',
    validator: v => ['none', 'sm', 'md', 'lg'].includes(v),
  },
  bodyClass: {
    type: String,
    default: '',
  },
})

const paddingClasses = computed(() => {
  return {
    none: 'p-0',
    sm: 'p-3 sm:p-4',
    md: 'p-4 sm:p-5',
    lg: 'p-5 sm:p-6',
  }[props.padding]
})
</script>
