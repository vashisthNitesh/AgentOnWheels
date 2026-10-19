<template>
  <TooltipProvider :delay-duration="delay">
    <TooltipRoot>
      <TooltipTrigger as-child>
        <slot />
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent
          :side="side"
          :side-offset="6"
          :class="cn(
            'z-tooltip rounded-md bg-slate-900 px-2.5 py-1 text-xs text-white shadow-md select-none',
            'dark:bg-slate-800 dark:border dark:border-border-default',
            'animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95',
            $attrs.class
          )"
        >
          <slot name="content">{{ content }}</slot>
          <TooltipArrow class="fill-slate-900 dark:fill-slate-800" />
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
})
</script>
