<template>
  <Toaster
    :theme="isDark ? 'dark' : 'light'"
    :position="position"
    :max-toasts="3"
    :close-button="true"
    :toast-options="{
      classes: {
        toast: 'bg-surface border border-border-default text-primary shadow-lg rounded-lg font-sans text-xs',
        description: 'text-secondary text-[11px]',
        actionButton: 'bg-primary-600 text-white font-medium text-xs px-2.5 py-1 rounded-md shadow-xs',
        cancelButton: 'bg-subtle text-secondary font-medium text-xs px-2.5 py-1 rounded-md',
      },
    }"
  />
</template>

<script setup>
import { computed } from 'vue'
import { Toaster } from 'vue-sonner'
import { useBreakpoints, breakpointsTailwind } from '@vueuse/core'
import { useTheme } from '../../composables/useTheme'

const { isDark } = useTheme()
const breakpoints = useBreakpoints(breakpointsTailwind)
const isMobile = breakpoints.smaller('md')

const position = computed(() => {
  return isMobile.value ? 'top-center' : 'bottom-right'
})
</script>
