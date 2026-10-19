<template>
  <kbd
    :class="cn(
      'inline-flex items-center justify-center rounded px-1.5 py-0.5 font-mono text-[11px] font-medium tracking-tight',
      'bg-subtle text-secondary border border-border-strong shadow-xs select-none',
      $attrs.class
    )"
  >
    <slot />
  </kbd>
</template>

<script setup>
import { cn } from '../../utils/cn'
</script>
