<template>
  <div class="inline-flex items-center justify-end w-full" @click.stop>
    <DropdownMenu :items="menuItems" align="end">
      <template #trigger>
        <button
          type="button"
          class="inline-flex items-center justify-center h-7 w-7 rounded-md text-slate-500 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500/20"
          title="Actions"
        >
          <MoreHorizontal class="h-4 w-4" />
        </button>
      </template>
    </DropdownMenu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { MoreHorizontal, Eye, Pencil, Copy, Trash2 } from 'lucide-vue-next'
import DropdownMenu from '../../ui/DropdownMenu.vue'
import { useConfirm } from '../../../composables/useConfirm'

const props = defineProps({
  row: {
    type: Object,
    required: true,
  },
  resourceKey: {
    type: String,
    required: true,
  },
  meta: Object,
  customActions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['view', 'edit', 'duplicate', 'delete', 'action'])

const router = useRouter()
const confirm = useConfirm()

const detailUrl = computed(() => {
  return props.resourceKey === 'orders' ? `/orders/${props.row.id}` : `/r/${props.resourceKey}/${props.row.id}`
})

const editUrl = computed(() => {
  return `/r/${props.resourceKey}/${props.row.id}/edit`
})

const menuItems = computed(() => {
  const items = [
    {
      label: 'View details',
      icon: Eye,
      action: () => {
        emit('view', props.row)
        router.push(detailUrl.value)
      },
    },
  ]

  if (props.meta?.create !== false && !props.meta?.readonly) {
    items.push({
      label: 'Edit',
      icon: Pencil,
      action: () => {
        emit('edit', props.row)
        router.push(editUrl.value)
      },
    })
    items.push({
      label: 'Duplicate',
      icon: Copy,
      action: () => {
        emit('duplicate', props.row)
      },
    })
  }

  // Custom actions
  if (props.customActions.length > 0) {
    items.push({ separator: true })
    props.customActions.forEach((act) => {
      items.push({
        label: act.label,
        icon: act.icon,
        danger: act.danger,
        action: () => emit('action', { action: act.name, row: props.row }),
      })
    })
  }

  // Delete
  if (props.meta?.create !== false && !props.meta?.readonly) {
    items.push({ separator: true })
    items.push({
      label: 'Delete',
      icon: Trash2,
      danger: true,
      action: async () => {
        const confirmed = await confirm.danger({
          title: `Delete ${props.meta?.title ? props.meta.title.slice(0, -1) : 'record'}?`,
          message: `Are you sure you want to delete this record? This action cannot be undone.`,
          confirmText: 'Delete',
        })
        if (confirmed) {
          emit('delete', props.row)
        }
      },
    })
  }

  return items
})
</script>
