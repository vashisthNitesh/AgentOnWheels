<template>
  <!-- Error / 404 State -->
  <div v-if="error" class="max-w-5xl mx-auto p-6 sm:p-12 text-center">
    <EmptyState
      title="Record Not Found"
      :description="error"
      :action-label="`Back to ${meta?.title || 'List'}`"
      @action="$router.push(`/r/${resourceKey}`)"
    />
  </div>

  <!-- Loading Skeletons -->
  <div v-else-if="loading || !record || !meta" class="max-w-6xl mx-auto p-4 sm:p-8 space-y-6">
    <div class="h-6 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
    <div class="flex justify-between items-center">
      <div class="h-10 w-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      <div class="h-10 w-44 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
    </div>
    <div class="h-96 w-full bg-slate-100 dark:bg-slate-900 rounded-xl animate-pulse" />
  </div>

  <!-- Main Resource Detail View -->
  <div v-else class="max-w-6xl mx-auto p-4 sm:p-8 space-y-6">
    <!-- Top Breadcrumb -->
    <div class="flex items-center justify-between">
      <router-link
        :to="`/r/${resourceKey}`"
        class="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors"
      >
        <ArrowLeft class="w-4 h-4" />
        <span>Back to {{ meta.title }}</span>
      </router-link>

      <span class="text-xs text-slate-400 font-mono">{{ meta.group }}</span>
    </div>

    <!-- Header Card -->
    <div class="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <!-- Title & Status -->
        <div class="space-y-1.5">
          <div class="flex flex-wrap items-center gap-2.5">
            <span class="text-2xl">{{ meta.icon || '📄' }}</span>
            <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              {{ record.display || record.name || record.plate_number || record.number || `#${record.id}` }}
            </h1>
            <CopyButton
              v-if="record.number || record.code || record.id"
              :text="String(record.number || record.code || record.id)"
            />
            <StatusPill
              v-if="meta.status && record[meta.status]"
              :status="record[meta.status]"
              :label="record[meta.status + '_label']"
              size="md"
            />
          </div>

          <p class="text-xs text-slate-500 dark:text-slate-400">
            {{ meta.title.slice(0, -1) }} record ID: <span class="font-mono font-medium text-slate-700 dark:text-slate-300">#{{ record.id }}</span>
          </p>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-wrap items-center gap-2">
          <!-- Special Action: Driver Passcode -->
          <Button
            v-if="resourceKey === 'drivers'"
            variant="outline"
            size="sm"
            @click="setDriverPasscode"
          >
            <Lock class="w-3.5 h-3.5 mr-1.5 text-slate-500" />
            <span>Set Passcode</span>
          </Button>

          <!-- Special Action: Download Report -->
          <Button
            v-if="resourceKey === 'reports'"
            variant="outline"
            size="sm"
            @click="downloadReport"
          >
            <Download class="w-3.5 h-3.5 mr-1.5 text-slate-500" />
            <span>Download CSV</span>
          </Button>

          <!-- Edit Button -->
          <router-link
            v-if="meta.create !== false && !meta.readonly"
            :to="`/r/${resourceKey}/${record.id}/edit`"
          >
            <Button variant="primary" size="sm">
              <Pencil class="w-3.5 h-3.5 mr-1.5" />
              <span>Edit</span>
            </Button>
          </router-link>

          <!-- Dropdown Menu for Secondary Actions -->
          <DropdownMenu :items="secondaryMenuItems" align="end">
            <template #trigger>
              <button
                type="button"
                class="inline-flex items-center justify-center h-8 w-8 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors shadow-xs"
                title="More Actions"
              >
                <MoreVertical class="w-4 h-4" />
              </button>
            </template>
          </DropdownMenu>
        </div>
      </div>
    </div>

    <!-- URL-Synced Navigation Tabs -->
    <Tabs
      v-model="activeTab"
      :tabs="detailTabs"
      class="border-b border-slate-200 dark:border-slate-800"
    />

    <!-- TAB 1: OVERVIEW -->
    <div v-if="activeTab === 'overview'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Info Cards Column -->
      <div class="lg:col-span-2 space-y-6">
        <Card class="p-6 space-y-4">
          <div class="border-b border-slate-100 dark:border-slate-800 pb-3">
            <h2 class="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              General Information
            </h2>
          </div>

          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4 text-xs">
            <div
              v-for="f in primaryFields"
              :key="f.name"
              class="space-y-1 p-2.5 rounded-lg bg-slate-50/70 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/60"
            >
              <dt class="text-[11px] font-medium text-slate-400">
                {{ f.label }}
              </dt>
              <dd class="text-xs font-semibold text-slate-900 dark:text-slate-100">
                <CellDispatcher
                  :row="record"
                  :name="f.name"
                  :field="f"
                  :resource-key="resourceKey"
                />
              </dd>
            </div>
          </dl>
        </Card>

        <!-- Secondary Fields if any -->
        <Card v-if="secondaryFields.length > 0" class="p-6 space-y-4">
          <div class="border-b border-slate-100 dark:border-slate-800 pb-3">
            <h2 class="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Configuration & Attributes
            </h2>
          </div>

          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4 text-xs">
            <div
              v-for="f in secondaryFields"
              :key="f.name"
              class="space-y-1 p-2.5 rounded-lg bg-slate-50/70 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/60"
            >
              <dt class="text-[11px] font-medium text-slate-400">
                {{ f.label }}
              </dt>
              <dd class="text-xs font-semibold text-slate-900 dark:text-slate-100">
                <CellDispatcher
                  :row="record"
                  :name="f.name"
                  :field="f"
                  :resource-key="resourceKey"
                />
              </dd>
            </div>
          </dl>
        </Card>
      </div>

      <!-- Right Sidebar Column -->
      <div class="space-y-6">
        <!-- Quick Meta Card -->
        <Card class="p-5 space-y-3 text-xs">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
            Record Status
          </h3>
          <div class="space-y-2">
            <div v-if="meta.status" class="flex justify-between items-center">
              <span class="text-slate-400">Status:</span>
              <StatusPill
                :status="record[meta.status]"
                :label="record[meta.status + '_label']"
                size="sm"
              />
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Module:</span>
              <span class="font-medium text-slate-800 dark:text-slate-200">{{ meta.title }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Domain:</span>
              <span class="font-medium text-slate-800 dark:text-slate-200">{{ meta.group }}</span>
            </div>
          </div>
        </Card>

        <!-- Audit Trail Card -->
        <Card class="p-5 space-y-2 text-xs">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
            System Timestamps
          </h3>
          <div class="space-y-2 text-[11px] text-slate-500 dark:text-slate-400">
            <p v-if="record.created_at">
              Created: <span class="font-medium text-slate-800 dark:text-slate-200">{{ formatDateTime(record.created_at) }}</span>
            </p>
            <p v-if="record.updated_at">
              Updated: <span class="font-medium text-slate-800 dark:text-slate-200">{{ formatDateTime(record.updated_at) }}</span>
            </p>
          </div>
        </Card>
      </div>
    </div>

    <!-- TAB 2: ACTIVITY -->
    <div v-else-if="activeTab === 'activity'" class="space-y-4">
      <ActivityTimeline :items="activityItems" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  Pencil,
  MoreVertical,
  Lock,
  Download,
  Copy,
  Trash2,
  Share2,
} from 'lucide-vue-next'
import api, { errText } from '../api'
import { formatDateTime } from '../utils/format'
import { useToast } from '../composables/useToast'
import { useConfirm } from '../composables/useConfirm'

import Card from '../components/ui/Card.vue'
import Button from '../components/ui/Button.vue'
import Tabs from '../components/ui/Tabs.vue'
import StatusPill from '../components/ui/StatusPill.vue'
import CopyButton from '../components/ui/CopyButton.vue'
import DropdownMenu from '../components/ui/DropdownMenu.vue'
import EmptyState from '../components/feedback/EmptyState.vue'
import CellDispatcher from '../components/data-table/cells/CellDispatcher.vue'
import ActivityTimeline from '../components/detail/ActivityTimeline.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const confirm = useConfirm()

const resourceKey = computed(() => route.params.key)
const recordId = computed(() => route.params.id)

const meta = ref(null)
const record = ref(null)
const loading = ref(true)
const error = ref('')

// URL-Synced Tabs
const activeTab = ref(route.query.tab || 'overview')
watch(activeTab, (t) => {
  router.replace({ query: { ...route.query, tab: t === 'overview' ? undefined : t } }).catch(() => {})
})

const detailTabs = computed(() => {
  return [
    { value: 'overview', label: 'Overview' },
    { value: 'activity', label: 'Audit Trail' },
  ]
})

// Partition fields into primary and secondary
const allFields = computed(() => {
  if (!meta.value?.fields) return []
  return Object.values(meta.value.fields).filter((f) => f.name !== 'id')
})

const primaryFields = computed(() => allFields.value.slice(0, 10))
const secondaryFields = computed(() => allFields.value.slice(10))

const activityItems = computed(() => {
  if (!record.value) return []
  const items = [
    {
      id: 'created',
      title: 'Record Created',
      description: `${meta.value?.title ? meta.value.title.slice(0, -1) : 'Item'} initialized in database`,
      timestamp: record.value.created_at || new Date().toISOString(),
      actor: record.value.created_by || 'System',
      tone: 'success',
    },
  ]
  if (record.value.updated_at && record.value.updated_at !== record.value.created_at) {
    items.push({
      id: 'updated',
      title: 'Record Updated',
      description: 'Attribute values were modified',
      timestamp: record.value.updated_at,
      actor: 'Admin',
      tone: 'info',
    })
  }
  return items
})

const secondaryMenuItems = computed(() => {
  const items = [
    {
      label: 'Duplicate record',
      icon: Copy,
      action: () => {
        router.push({
          path: `/r/${resourceKey.value}/new`,
          query: { duplicate_from: record.value.id },
        })
      },
    },
    {
      label: 'Share link',
      icon: Share2,
      action: () => {
        navigator.clipboard?.writeText(window.location.href)
        toast.success('Direct link copied to clipboard')
      },
    },
  ]

  if (meta.value?.create !== false && !meta.value?.readonly) {
    items.push({ separator: true })
    items.push({
      label: 'Delete record',
      icon: Trash2,
      danger: true,
      action: async () => {
        const ok = await confirm.danger({
          title: `Delete ${meta.value?.title ? meta.value.title.slice(0, -1) : 'record'}?`,
          message: 'Are you sure you want to delete this record? This action cannot be undone.',
          confirmText: 'Delete',
        })
        if (ok) {
          try {
            await api.delete(`${resourceKey.value}/${record.value.id}/`)
            toast.success('Record deleted')
            router.push(`/r/${resourceKey.value}`)
          } catch (e) {
            toast.error(`Delete failed: ${errText(e)}`)
          }
        }
      },
    })
  }

  return items
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [metaRes, recRes] = await Promise.all([
      api.get(`meta/${resourceKey.value}/`),
      api.get(`${resourceKey.value}/${recordId.value}/`),
    ])
    meta.value = metaRes.data
    record.value = recRes.data
  } catch (e) {
    if (e.response?.status === 404) {
      error.value = 'Record not found or access denied.'
    } else {
      error.value = errText(e)
    }
  } finally {
    loading.value = false
  }
}

async function setDriverPasscode() {
  const pass = prompt('New 6+ digit passcode for driver mobile app:')
  if (!pass) return
  try {
    await api.post(`drivers/${recordId.value}/set_passcode/`, { passcode: pass })
    toast.success('Passcode updated successfully')
    loadData()
  } catch (e) {
    toast.error(`Failed to update passcode: ${errText(e)}`)
  }
}

async function downloadReport() {
  try {
    const res = await api.get(`reports/${recordId.value}/download/`, { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `${record.value.number || 'report'}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Report downloaded')
  } catch (e) {
    toast.error(`Download failed: ${errText(e)}`)
  }
}

watch([resourceKey, recordId], () => {
  loadData()
})

onMounted(() => {
  loadData()
})
</script>
