<template>
  <Drawer
    :open="open"
    :title="drawerTitle"
    :description="drawerSubtitle"
    width="md"
    @update:open="$emit('update:open', $event)"
  >
    <div v-if="record" class="space-y-6 py-2">
      <!-- Status & Top Badges -->
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-2">
          <StatusPill
            v-if="statusValue"
            :status="statusValue"
            :label="record.status_label"
            size="md"
          />
          <span v-if="record.number || record.code" class="font-mono text-xs font-semibold text-slate-700 dark:text-slate-300">
            #{{ record.number || record.code }}
          </span>
        </div>

        <router-link
          :to="detailUrl"
          class="inline-flex items-center gap-1 text-xs font-medium text-brand-600 dark:text-brand-400 hover:underline"
        >
          <span>Open full page</span>
          <ExternalLink class="w-3.5 h-3.5" />
        </router-link>
      </div>

      <!-- Key Fields Grid -->
      <div class="space-y-4">
        <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Record Details
        </h4>
        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          <div
            v-for="col in keyColumns"
            :key="col.name"
            class="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800"
          >
            <dt class="text-[11px] font-medium text-slate-500 dark:text-slate-400">
              {{ col.label }}
            </dt>
            <dd class="mt-1 text-xs font-semibold text-slate-900 dark:text-slate-100">
              <CellDispatcher
                :row="record"
                :name="col.name"
                :field="meta?.fields?.[col.name]"
                :resource-key="resourceKey"
              />
            </dd>
          </div>
        </dl>
      </div>

      <!-- Timestamps -->
      <div v-if="record.created_at || record.updated_at" class="pt-4 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500 space-y-1">
        <p v-if="record.created_at">
          Created: {{ formatDateTime(record.created_at) }}
        </p>
        <p v-if="record.updated_at">
          Last updated: {{ formatDateTime(record.updated_at) }}
        </p>
      </div>
    </div>

    <!-- Drawer Footer -->
    <template #footer>
      <div class="flex items-center justify-between w-full">
        <Button variant="ghost" size="sm" @click="$emit('update:open', false)">
          Close
        </Button>
        <div class="flex items-center gap-2">
          <Button
            v-if="meta?.create !== false && !meta?.readonly"
            variant="outline"
            size="sm"
            @click="onEdit"
          >
            <Pencil class="h-3.5 w-3.5" />
            Edit
          </Button>
          <Button as="router-link" :to="detailUrl" variant="primary" size="sm">
            Open full page
            <ExternalLink class="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </template>
  </Drawer>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ExternalLink, Pencil } from 'lucide-vue-next'
import Drawer from '../ui/Drawer.vue'
import Button from '../ui/Button.vue'
import StatusPill from '../ui/StatusPill.vue'
import CellDispatcher from '../data-table/cells/CellDispatcher.vue'
import { formatDateTime } from '../../utils/format'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  record: {
    type: Object,
    default: null,
  },
  resourceKey: {
    type: String,
    required: true,
  },
  meta: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:open'])
const router = useRouter()

const drawerTitle = computed(() => {
  if (!props.record) return 'Quick View'
  const t = props.meta?.title || 'Record'
  const singular = t.endsWith('ies') ? `${t.slice(0, -3)}y` : t.endsWith('s') ? t.slice(0, -1) : t
  return `${singular} details`
})

const drawerSubtitle = computed(() => {
  if (!props.record) return ''
  return props.record.number || props.record.name || props.record.plate_number || `ID: ${props.record.id}`
})

const statusValue = computed(() => {
  const statusField = props.meta?.status || 'status'
  return props.record?.[statusField] || null
})

const detailUrl = computed(() => {
  if (!props.record) return '#'
  return props.resourceKey === 'orders' ? `/orders/${props.record.id}` : `/r/${props.resourceKey}/${props.record.id}`
})

const editUrl = computed(() => {
  if (!props.record) return '#'
  return `/r/${props.resourceKey}/${props.record.id}/edit`
})

const keyColumns = computed(() => {
  if (!props.meta?.columns) return []
  return props.meta.columns.slice(0, 8).map((colName) => ({
    name: colName,
    label: props.meta.fields?.[colName]?.label || colName.replace(/_/g, ' '),
  }))
})

function onEdit() {
  emit('update:open', false)
  router.push(editUrl.value)
}
</script>
