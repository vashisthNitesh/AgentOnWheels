<template>
  <div :class="cn('flex flex-col items-center justify-center p-8 sm:p-12 text-center select-none', $attrs.class)">
    <!-- SVG Themed Illustration -->
    <div class="relative w-24 h-24 mb-4 flex items-center justify-center rounded-2xl bg-subtle border border-border-default shadow-xs text-secondary">
      <!-- Variant 1: No Data -->
      <svg v-if="variant === 'no-data'" class="w-12 h-12 text-primary-500/80 stroke-current" fill="none" viewBox="0 0 24 24" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
      </svg>

      <!-- Variant 2: No Results for Filters -->
      <svg v-else-if="variant === 'no-results'" class="w-12 h-12 text-amber-500/80 stroke-current" fill="none" viewBox="0 0 24 24" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z" />
      </svg>

      <!-- Variant 3: No Permission -->
      <svg v-else-if="variant === 'no-permission'" class="w-12 h-12 text-rose-500/80 stroke-current" fill="none" viewBox="0 0 24 24" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
      </svg>

      <!-- Variant 4: Error with Retry -->
      <svg v-else class="w-12 h-12 text-danger-500/80 stroke-current" fill="none" viewBox="0 0 24 24" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
      </svg>
    </div>

    <!-- Title -->
    <h3 class="text-base font-semibold text-primary max-w-md">
      {{ computedTitle }}
    </h3>

    <!-- Description -->
    <p class="text-xs text-secondary mt-1.5 max-w-sm">
      {{ computedDescription }}
    </p>

    <!-- Call to Actions -->
    <div class="mt-5 flex flex-wrap items-center justify-center gap-3">
      <slot name="actions">
        <Button
          v-if="actionText || defaultAction"
          variant="primary"
          size="sm"
          @click="$emit('action')"
        >
          {{ actionText || defaultAction }}
        </Button>

        <Button
          v-if="secondaryText"
          variant="ghost"
          size="sm"
          @click="$emit('secondary-action')"
        >
          {{ secondaryText }}
        </Button>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { cn } from '../../utils/cn'
import Button from '../ui/Button.vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'no-data',
    validator: v => ['no-data', 'no-results', 'no-permission', 'error'].includes(v),
  },
  title: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
  actionText: {
    type: String,
    default: '',
  },
  secondaryText: {
    type: String,
    default: '',
  },
})

defineEmits(['action', 'secondary-action'])

const computedTitle = computed(() => {
  if (props.title) return props.title
  return {
    'no-data': 'No records found',
    'no-results': 'No results match your filters',
    'no-permission': 'Access restricted',
    'error': 'Something went wrong',
  }[props.variant]
})

const computedDescription = computed(() => {
  if (props.description) return props.description
  return {
    'no-data': 'Get started by creating your first entry.',
    'no-results': 'Try broadening your search term or clearing applied filters.',
    'no-permission': 'You do not have permission to view this resource.',
    'error': 'An unexpected error occurred while loading this data. Please try again.',
  }[props.variant]
})

const defaultAction = computed(() => {
  return {
    'no-data': 'Create entry',
    'no-results': 'Clear filters',
    'no-permission': 'Back to dashboard',
    'error': 'Retry',
  }[props.variant]
})
</script>
