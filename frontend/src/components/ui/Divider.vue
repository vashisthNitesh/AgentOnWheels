<template>
  <div
    role="separator"
    :aria-orientation="orientation"
    :class="cn(
      orientation === 'vertical'
        ? 'inline-block h-full w-[1px] min-h-[1em] bg-border-default self-stretch'
        : 'block w-full h-[1px] bg-border-default my-4',
      $attrs.class
    )"
  />
</template>

<script setup>
import { cn } from '../../utils/cn'

defineProps({
  orientation: {
    type: String,
    default: 'horizontal',
    validator: v => ['horizontal', 'vertical'].includes(v),
  },
})
</script>
