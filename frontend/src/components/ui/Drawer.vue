<template>
  <DialogRoot :open="open" @update:open="onUpdateOpen">
    <DialogTrigger v-if="$slots.trigger" as-child>
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-drawer bg-slate-950/40 backdrop-blur-[2px] animate-in fade-in-0 duration-200" />

      <DialogContent
        :class="cn(
          'fixed inset-y-0 right-0 z-drawer flex h-full w-full flex-col border-l border-border-default bg-surface text-primary shadow-xl outline-none',
          'animate-in slide-in-from-right duration-250',
          widthClasses,
          $attrs.class
        )"
      >
        <header class="flex shrink-0 items-start justify-between gap-4 border-b border-border-default px-5 py-4">
          <slot name="header">
            <div class="min-w-0 space-y-0.5">
              <DialogTitle class="truncate text-base font-semibold text-primary">
                <slot name="title">{{ title }}</slot>
              </DialogTitle>
              <DialogDescription v-if="description || $slots.description" class="text-xs text-muted">
                <slot name="description">{{ description }}</slot>
              </DialogDescription>
            </div>
          </slot>

          <DialogClose
            class="-mr-1.5 shrink-0 rounded-md p-1.5 text-muted transition hover:bg-subtle hover:text-primary focus-ring"
            aria-label="Close"
          >
            <X class="h-4 w-4" />
          </DialogClose>
        </header>

        <div class="min-h-0 flex-1 overflow-y-auto px-5 py-5">
          <slot />
        </div>

        <footer
          v-if="$slots.footer"
          class="flex shrink-0 items-center justify-end gap-2.5 border-t border-border-default bg-subtle/60 px-5 py-3"
        >
          <slot name="footer" />
        </footer>
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

defineOptions({ inheritAttrs: false })

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  width: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg', 'full'].includes(v),
  },
})

const emit = defineEmits(['update:open', 'close'])

const widthClasses = computed(() => ({
  sm: 'sm:max-w-[400px]',
  md: 'sm:max-w-[520px]',
  lg: 'sm:max-w-[720px]',
  full: 'max-w-full',
}[props.width]))

function onUpdateOpen(val) {
  emit('update:open', val)
  if (!val) emit('close')
}
</script>
