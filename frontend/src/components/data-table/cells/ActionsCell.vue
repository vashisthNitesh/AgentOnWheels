<template>
  <div class="flex items-center justify-end gap-0.5" @click.stop>
    <Tooltip v-if="canEdit" content="Edit" :delay="500">
      <button
        type="button"
        class="inline-flex h-7 w-7 items-center justify-center rounded-md text-muted opacity-70 transition hover:bg-slate-200/70 hover:text-primary group-hover:opacity-100 focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/50 dark:hover:bg-slate-700"
        :aria-label="`Edit ${label}`"
        @click="$emit('edit', row)"
      >
        <Pencil class="h-3.5 w-3.5" />
      </button>
    </Tooltip>

    <DropdownMenu :items="menuItems" align="end">
      <template #trigger>
        <button
          type="button"
          class="inline-flex h-7 w-7 items-center justify-center rounded-md text-muted transition hover:bg-slate-200/70 hover:text-primary data-[state=open]:bg-slate-200/70 data-[state=open]:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/50 dark:hover:bg-slate-700 dark:data-[state=open]:bg-slate-700"
          :aria-label="`More actions for ${label}`"
        >
          <MoreHorizontal class="h-4 w-4" />
        </button>
      </template>
    </DropdownMenu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MoreHorizontal, Eye, Pencil, Copy, Trash2, ExternalLink } from 'lucide-vue-next'
import DropdownMenu from '../../ui/DropdownMenu.vue'
import Tooltip from '../../ui/Tooltip.vue'
import { useConfirm } from '../../../composables/useConfirm'

const props = defineProps({
  row: { type: Object, required: true },
  resourceKey: { type: String, required: true },
  meta: Object,
  customActions: { type: Array, default: () => [] },
})

const emit = defineEmits(['view', 'edit', 'duplicate', 'delete', 'action'])
const confirm = useConfirm()

const canEdit = computed(() => props.meta?.create !== false && !props.meta?.readonly)
const label = computed(() => props.row.number || props.row.code || props.row.name || `#${props.row.id}`)

const singular = computed(() => {
  const t = props.meta?.title || 'record'
  return (t.endsWith('ies') ? `${t.slice(0, -3)}y` : t.endsWith('s') ? t.slice(0, -1) : t).toLowerCase()
})

const detailUrl = computed(() =>
  props.resourceKey === 'orders' ? `/orders/${props.row.id}` : `/r/${props.resourceKey}/${props.row.id}`
)

const menuItems = computed(() => {
  const items = [
    { label: 'View details', icon: Eye, action: () => emit('view', props.row) },
    { label: 'Open in new tab', icon: ExternalLink, action: () => window.open(detailUrl.value, '_blank', 'noopener') },
  ]

  if (canEdit.value) {
    items.push({ label: 'Edit', icon: Pencil, action: () => emit('edit', props.row) })
    items.push({ label: 'Duplicate', icon: Copy, action: () => emit('duplicate', props.row) })
  }

  if (props.customActions.length) {
    items.push({ separator: true })
    for (const act of props.customActions) {
      items.push({
        label: act.label,
        icon: act.icon,
        danger: act.danger,
        action: () => emit('action', { action: act.name, row: props.row }),
      })
    }
  }

  if (canEdit.value) {
    items.push({ separator: true })
    items.push({
      label: 'Delete',
      icon: Trash2,
      danger: true,
      action: async () => {
        const ok = await confirm.danger({
          title: `Delete ${singular.value} ${label.value}?`,
          message: 'This permanently removes the record. This action cannot be undone.',
          confirmText: 'Delete',
        })
        if (ok) emit('delete', props.row)
      },
    })
  }

  return items
})
</script>
