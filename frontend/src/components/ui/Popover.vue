<template>
  <PopoverRoot :open="open" @update:open="$emit('update:open', $event)">
    <PopoverTrigger as-child>
      <slot name="trigger" />
    </PopoverTrigger>
    <PopoverPortal>
      <PopoverContent
        :side="side"
        :align="align"
        :side-offset="sideOffset"
        :class="cn(
          'z-dropdown rounded-lg border border-border-default bg-surface-raised p-4 text-primary shadow-lg outline-none',
          'animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95',
          $attrs.class
        )"
      >
        <slot />
        <PopoverClose
          v-if="showClose"
          class="absolute right-2.5 top-2.5 text-secondary hover:text-primary transition p-1 rounded focus-ring"
          aria-label="Close"
        >
          <X class="w-3.5 h-3.5" />
        </PopoverClose>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>

<script setup>
import {
  PopoverRoot,
  PopoverTrigger,
  PopoverPortal,
  PopoverContent,
  PopoverClose,
} from 'reka-ui'
import { X } from 'lucide-vue-next'
import { cn } from '../../utils/cn'

defineProps({
  open: {
    type: Boolean,
    default: undefined,
  },
  side: {
    type: String,
    default: 'bottom',
    validator: v => ['top', 'right', 'bottom', 'left'].includes(v),
  },
  align: {
    type: String,
    default: 'center',
    validator: v => ['start', 'center', 'end'].includes(v),
  },
  sideOffset: {
    type: Number,
    default: 6,
  },
  showClose: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['update:open'])
</script>
