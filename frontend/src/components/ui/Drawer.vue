<template>
  <DialogRoot :open="open" @update:open="onUpdateOpen">
    <DialogTrigger v-if="$slots.trigger" as-child>
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <!-- Backdrop Overlay -->
      <DialogOverlay
        class="fixed inset-0 z-drawer bg-slate-950/50 backdrop-blur-xs transition-opacity animate-in fade-in duration-250"
      />

      <!-- Right Drawer Panel -->
      <DialogContent
        :class="cn(
          'fixed inset-y-0 right-0 z-drawer h-full w-full bg-surface text-primary shadow-2xl border-l border-border-default flex flex-col',
          'animate-in slide-in-from-right duration-250 ease-out',
          widthClasses,
          $attrs.class
        )"
      >
        <!-- Drawer Header -->
        <div class="flex items-center justify-between p-5 border-b border-border-default bg-surface shrink-0">
          <slot name="header">
            <div class="space-y-0.5 pr-4">
              <DialogTitle class="text-base font-semibold text-primary">
                <slot name="title">{{ title }}</slot>
              </DialogTitle>
              <DialogDescription v-if="description || $slots.description" class="text-xs text-secondary">
                <slot name="description">{{ description }}</slot>
              </DialogDescription>
            </div>
          </slot>

          <DialogClose
            class="rounded-md p-1.5 text-secondary hover:text-primary hover:bg-subtle transition focus-ring ml-auto shrink-0"
            aria-label="Close drawer"
          >
            <X class="w-4 h-4" />
          </DialogClose>
        </div>

        <!-- Drawer Body (Scrollable) -->
        <div class="p-5 overflow-y-auto flex-1">
          <slot />
        </div>

        <!-- Drawer Footer (Sticky) -->
        <div
          v-if="$slots.footer"
          class="p-4 border-t border-border-default bg-subtle/50 flex items-center justify-end gap-2.5 shrink-0"
        >
          <slot name="footer" />
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<script setup>
import { computed } from 'vue'
import {
  DialogRoot,
  DialogTrigger,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from 'reka-ui'
import { X } from 'lucide-vue-next'
import { cn } from '../../utils/cn'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
  width: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg', 'full'].includes(v),
  },
})

const emit = defineEmits(['update:open', 'close'])

const widthClasses = computed(() => {
  return {
    sm: 'max-w-[420px]',
    md: 'max-w-[560px]',
    lg: 'max-w-[720px]',
    full: 'max-w-full',
  }[props.width]
})

function onUpdateOpen(val) {
  emit('update:open', val)
  if (!val) emit('close')
}
</script>
