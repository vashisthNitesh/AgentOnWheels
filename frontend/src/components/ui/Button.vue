<template>
  <component
    :is="componentType"
    :to="as === 'router-link' ? to : undefined"
    :href="as === 'a' ? href : undefined"
    :type="as === 'button' ? type : undefined"
    :disabled="as === 'button' ? (disabled || loading) : undefined"
    :aria-disabled="(disabled || loading) ? 'true' : undefined"
    :aria-busy="loading ? 'true' : undefined"
    :tabindex="(disabled || loading) ? -1 : undefined"
    :class="cn(
      buttonVariants({ variant, size, block, loading }),
      loading && 'pointer-events-none cursor-wait opacity-70',
      disabled && 'opacity-50 cursor-not-allowed pointer-events-none',
      $attrs.class
    )"
    @click.capture="handleClick"
  >
    <!-- Loading spinner replaces leading icon without layout jump -->
    <Spinner v-if="loading" :size="size === 'lg' ? 'md' : 'sm'" class="shrink-0" />
    <component
      :is="leadingIcon"
      v-else-if="leadingIcon"
      :class="cn('shrink-0', size === 'lg' ? 'w-5 h-5' : 'w-4 h-4')"
    />

    <span v-if="$slots.default" class="truncate inline-flex items-center gap-1.5">
      <slot />
    </span>

    <component
      :is="trailingIcon"
      v-if="trailingIcon && !loading"
      :class="cn('shrink-0', size === 'lg' ? 'w-5 h-5' : 'w-4 h-4')"
    />
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { cva } from 'class-variance-authority'
import { cn } from '../../utils/cn'
import Spinner from './Spinner.vue'

const buttonVariants = cva(
  'inline-flex items-center justify-center font-medium transition-all select-none active:scale-[0.98] focus-ring disabled:opacity-50 disabled:pointer-events-none cursor-pointer',
  {
    variants: {
      variant: {
        primary: 'bg-primary-600 text-white hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 shadow-xs border border-transparent',
        secondary: 'bg-surface text-primary border border-border-default hover:bg-subtle shadow-xs',
        ghost: 'bg-transparent text-secondary hover:text-primary hover:bg-subtle border border-transparent',
        outline: 'bg-transparent text-primary border border-border-strong hover:bg-subtle shadow-xs',
        danger: 'bg-danger-600 text-white hover:bg-danger-700 dark:bg-danger-500 dark:hover:bg-danger-600 shadow-xs border border-transparent',
        'danger-ghost': 'bg-transparent text-danger-600 hover:text-danger-700 hover:bg-danger-50 dark:text-danger-400 dark:hover:bg-danger-950/40 border border-transparent',
        link: 'bg-transparent text-primary-600 hover:text-primary-700 dark:text-primary-400 underline-offset-4 hover:underline p-0 h-auto border-0 shadow-none',
      },
      size: {
        sm: 'h-8 px-3 text-xs rounded-md gap-1.5',
        md: 'h-9 px-3.5 text-sm rounded-md gap-2',
        lg: 'h-10 px-4 text-sm rounded-md gap-2',
        icon: 'h-9 w-9 p-0 rounded-md',
        'icon-sm': 'h-8 w-8 p-0 rounded-md',
        'icon-lg': 'h-10 w-10 p-0 rounded-md',
      },
      block: {
        true: 'w-full',
      },
      loading: {
        true: 'cursor-wait',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
  },
  size: {
    type: String,
    default: 'md',
  },
  type: {
    type: String,
    default: 'button',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  block: {
    type: Boolean,
    default: false,
  },
  leadingIcon: {
    type: [Object, Function],
    default: null,
  },
  trailingIcon: {
    type: [Object, Function],
    default: null,
  },
  as: {
    type: String,
    default: 'button',
    validator: v => ['button', 'a', 'router-link'].includes(v),
  },
  to: {
    type: [String, Object],
    default: undefined,
  },
  href: {
    type: String,
    default: undefined,
  },
})

const componentType = computed(() => {
  if (props.as === 'router-link') return 'router-link'
  if (props.as === 'a') return 'a'
  return 'button'
})

function handleClick(e) {
  if (props.disabled || props.loading) {
    e.preventDefault()
    e.stopPropagation()
  }
}
</script>
