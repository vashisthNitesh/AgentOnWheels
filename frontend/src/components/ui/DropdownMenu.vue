<template>
  <DropdownMenuRoot :open="open" @update:open="$emit('update:open', $event)">
    <DropdownMenuTrigger as-child>
      <slot name="trigger" />
    </DropdownMenuTrigger>

    <DropdownMenuPortal>
      <DropdownMenuContent
        :side="side"
        :align="align"
        :side-offset="sideOffset"
        :class="cn(
          'z-dropdown min-w-[190px] rounded-lg border border-border-default bg-surface-raised p-1.5 text-primary shadow-lg outline-none select-none',
          'animate-in fade-in-80 zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2',
          $attrs.class
        )"
      >
        <slot>
          <template v-for="(item, idx) in items" :key="idx">
            <DropdownMenuSeparator
              v-if="item.separator || item.divider"
              class="my-1 h-[1px] bg-border-default"
            />
            <DropdownMenuLabel
              v-else-if="item.header || item.label && !item.action && !item.to"
              class="px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-muted"
            >
              {{ item.header || item.label }}
            </DropdownMenuLabel>
            <DropdownMenuItem
              v-else
              :disabled="item.disabled"
              :class="cn(
                'flex items-center justify-between gap-2 px-2.5 py-1.5 rounded-md text-xs font-medium cursor-pointer transition-colors outline-none',
                'hover:bg-subtle focus:bg-subtle',
                item.danger ? 'text-danger-600 hover:text-danger-700 hover:bg-danger-50 dark:hover:bg-danger-950/40' : 'text-primary',
                item.disabled && 'opacity-50 pointer-events-none'
              )"
              @click="handleAction(item)"
            >
              <div class="flex items-center gap-2 truncate">
                <component :is="item.icon" v-if="item.icon" class="w-3.5 h-3.5 shrink-0 opacity-80" />
                <span class="truncate">{{ item.label }}</span>
              </div>
              <span v-if="item.shortcut" class="font-mono text-[10px] text-muted ml-2">
                {{ item.shortcut }}
              </span>
            </DropdownMenuItem>
          </template>
        </slot>
      </DropdownMenuContent>
    </DropdownMenuPortal>
  </DropdownMenuRoot>
</template>

<script setup>
import {
  DropdownMenuRoot,
  DropdownMenuTrigger,
  DropdownMenuPortal,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from 'reka-ui'
import { useRouter } from 'vue-router'
import { cn } from '../../utils/cn'

const props = defineProps({
  open: {
    type: Boolean,
    default: undefined,
  },
  items: {
    type: Array,
    default: () => [],
  },
  side: {
    type: String,
    default: 'bottom',
    validator: v => ['top', 'right', 'bottom', 'left'].includes(v),
  },
  align: {
    type: String,
    default: 'end',
    validator: v => ['start', 'center', 'end'].includes(v),
  },
  sideOffset: {
    type: Number,
    default: 4,
  },
})

defineEmits(['update:open'])

const router = useRouter()

function handleAction(item) {
  if (item.action && typeof item.action === 'function') {
    item.action()
  } else if (item.to && router) {
    router.push(item.to)
  } else if (item.href) {
    window.location.href = item.href
  }
}
</script>
