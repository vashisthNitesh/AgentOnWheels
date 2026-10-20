<template>
  <DropdownMenuRoot :open="open" :modal="false" @update:open="$emit('update:open', $event)">
    <DropdownMenuTrigger as-child>
      <slot name="trigger" />
    </DropdownMenuTrigger>

    <DropdownMenuPortal>
      <DropdownMenuContent
        :side="side"
        :align="align"
        :side-offset="sideOffset"
        :collision-padding="12"
        :class="cn(floatingPanel, 'z-dropdown min-w-[200px] p-1 select-none', $attrs.class)"
      >
        <slot>
          <template v-for="(item, idx) in items" :key="idx">
            <DropdownMenuSeparator
              v-if="item.separator || item.divider"
              class="-mx-1 my-1 h-px bg-border-default"
            />
            <DropdownMenuLabel
              v-else-if="item.header"
              class="truncate px-2.5 pb-1 pt-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted"
            >
              {{ item.header }}
            </DropdownMenuLabel>
            <DropdownMenuItem
              v-else
              :disabled="item.disabled"
              :class="cn(
                'flex cursor-pointer items-center justify-between gap-3 rounded-md px-2.5 py-1.5 text-[13px] outline-none transition-colors',
                item.danger
                  ? 'text-danger-600 data-[highlighted]:bg-danger-50 data-[highlighted]:text-danger-700 dark:text-danger-500 dark:data-[highlighted]:bg-danger-500/10'
                  : 'text-primary data-[highlighted]:bg-subtle',
                'data-[disabled]:pointer-events-none data-[disabled]:opacity-50'
              )"
              @select="handleAction(item)"
            >
              <span class="flex min-w-0 items-center gap-2.5">
                <component :is="item.icon" v-if="item.icon" class="h-4 w-4 shrink-0 opacity-70" />
                <span class="truncate">{{ item.label }}</span>
              </span>
              <span v-if="item.shortcut" class="font-mono text-[10px] text-muted">{{ item.shortcut }}</span>
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
import { floatingPanel } from './controlStyles'

defineOptions({ inheritAttrs: false })

defineProps({
  open: { type: Boolean, default: undefined },
  items: { type: Array, default: () => [] },
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
  sideOffset: { type: Number, default: 6 },
})

defineEmits(['update:open'])

const router = useRouter()

function handleAction(item) {
  if (typeof item.action === 'function') item.action()
  else if (item.to) router.push(item.to)
  else if (item.href) window.location.href = item.href
}
</script>
