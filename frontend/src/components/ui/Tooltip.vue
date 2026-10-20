<template>
  <!-- When disabled or empty, render the trigger alone so no blank bubble appears. -->
  <slot v-if="disabled || (!content && !$slots.content)" />
  <TooltipProvider v-else :delay-duration="delay">
    <TooltipRoot>
      <TooltipTrigger as-child>
        <slot />
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent
          :side="side"
          :side-offset="6"
          :class="cn(
            'z-tooltip max-w-xs rounded-md bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-white shadow-md select-none',
            'dark:bg-slate-700',
            'animate-in fade-in-0 zoom-in-95',
            $attrs.class
          )"
        >
          <slot name="content">{{ content }}</slot>
          <TooltipArrow class="fill-slate-900 dark:fill-slate-700" />
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>

<script setup>
import {
  TooltipProvider,
  TooltipRoot,
  TooltipTrigger,
  TooltipPortal,
  TooltipContent,
  TooltipArrow,
} from 'reka-ui'
import { cn } from '../../utils/cn'

defineOptions({ inheritAttrs: false })

defineProps({
  content: {
    type: String,
    default: '',
  },
  delay: {
    type: Number,
    default: 300,
  },
  side: {
    type: String,
    default: 'top',
    validator: v => ['top', 'right', 'bottom', 'left'].includes(v),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})
</script>
