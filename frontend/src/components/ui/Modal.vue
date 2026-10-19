<template>
  <DialogRoot :open="open" @update:open="onUpdateOpen">
    <DialogTrigger v-if="$slots.trigger" as-child>
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <!-- Backdrop Overlay -->
      <DialogOverlay
        class="fixed inset-0 z-modal bg-slate-950/50 backdrop-blur-xs transition-opacity animate-in fade-in duration-200"
      />

      <!-- Dialog Content Box -->
      <div class="fixed inset-0 z-modal overflow-y-auto p-4 sm:p-6 flex min-h-full items-center justify-center pointer-events-none">
        <DialogContent
          :class="cn(
            'pointer-events-auto relative w-full rounded-xl border border-border-default bg-surface text-primary shadow-xl overflow-hidden flex flex-col',
            'animate-in fade-in-0 zoom-in-95 duration-200',
            sizeClasses,
            $attrs.class
          )"
          @pointer-down-outside="onPointerDownOutside"
          @escape-key-down="onEscapeKeyDown"
        >
          <!-- Modal Header -->
          <div
            v-if="title || $slots.header || $slots.title"
            class="flex items-start justify-between p-5 border-b border-border-default bg-surface shrink-0"
          >
            <slot name="header">
              <div class="space-y-1 pr-6">
                <DialogTitle class="text-base font-semibold text-primary">
                  <slot name="title">{{ title }}</slot>
                </DialogTitle>
                <DialogDescription v-if="description || $slots.description" class="text-xs text-secondary">
                  <slot name="description">{{ description }}</slot>
                </DialogDescription>
              </div>
            </slot>

            <DialogClose
              v-if="showClose"
              class="rounded-md p-1.5 text-secondary hover:text-primary hover:bg-subtle transition focus-ring absolute right-4 top-4"
              aria-label="Close dialog"
            >
              <X class="w-4 h-4" />
            </DialogClose>
          </div>

          <!-- Modal Body (Scrollable) -->
          <div class="p-5 overflow-y-auto max-h-[calc(85vh-130px)] flex-1">
            <slot />
          </div>

          <!-- Modal Footer (Sticky) -->
          <div
            v-if="$slots.footer"
            class="p-4 border-t border-border-default bg-subtle/50 flex items-center justify-end gap-2.5 shrink-0"
          >
            <slot name="footer" />
          </div>
        </DialogContent>
      </div>
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
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg', 'xl'].includes(v),
  },
  persistent: {
    type: Boolean,
    default: false,
  },
  showClose: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:open', 'close'])

const sizeClasses = computed(() => {
  return {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  }[props.size]
})

function onUpdateOpen(val) {
  emit('update:open', val)
  if (!val) emit('close')
}

function onPointerDownOutside(e) {
  if (props.persistent) {
    e.preventDefault()
  }
}

function onEscapeKeyDown(e) {
  if (props.persistent) {
    e.preventDefault()
  }
}
</script>
