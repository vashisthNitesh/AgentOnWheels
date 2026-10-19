<template>
  <div class="space-y-6 animate-in fade-in duration-200">
    <!-- Header -->
    <PageHeader
      title="Configuration Hub"
      subtitle="Master data, tax rules, fleet parameters, and system registries"
    >
      <template #actions>
        <div class="w-full sm:w-72">
          <Input
            v-model="q"
            placeholder="Filter configurations…"
            clearable
            size="sm"
          >
            <template #prefix>
              <Search class="w-4 h-4 text-muted" />
            </template>
          </Input>
        </div>
      </template>
    </PageHeader>

    <!-- Loading Skeleton Grid -->
    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div
        v-for="n in 8"
        :key="n"
        class="h-28 rounded-xl border border-border-default/60 bg-surface p-5 flex flex-col justify-between animate-pulse"
      >
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-subtle" />
          <div class="space-y-1.5 flex-1">
            <div class="h-4 w-3/4 bg-subtle rounded" />
            <div class="h-3 w-1/2 bg-subtle rounded" />
          </div>
        </div>
        <div class="h-3 w-1/3 bg-subtle rounded self-end" />
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="p-6 rounded-xl border border-danger-500/30 bg-danger-500/10 text-danger-700 dark:text-danger-400 text-sm flex items-center justify-between"
    >
      <div class="flex items-center gap-2">
        <AlertCircle class="w-5 h-5 shrink-0" />
        <span>Failed to load configuration registries: {{ error }}</span>
      </div>
      <Button size="sm" variant="outline" @click="fetchConfig">
        Retry
      </Button>
    </div>

    <!-- Empty Filter Result -->
    <div
      v-else-if="shown.length === 0"
      class="py-12 text-center rounded-xl border border-dashed border-border-strong bg-subtle/50"
    >
      <div class="w-12 h-12 rounded-full bg-subtle flex items-center justify-center mx-auto mb-3 text-secondary">
        <Search class="w-5 h-5" />
      </div>
      <p class="text-sm font-semibold text-primary">No matching configuration found</p>
      <p class="text-xs text-secondary mt-1">No registries match "{{ q }}". Try a different search term.</p>
      <Button
        v-if="q"
        size="sm"
        variant="outline"
        class="mt-4"
        @click="q = ''"
      >
        Clear filter
      </Button>
    </div>

    <!-- Configuration Cards Grid -->
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <router-link
        v-for="item in shown"
        :key="item.key"
        :to="'/r/' + item.key"
        class="group p-5 rounded-xl border border-border-default bg-surface hover:border-brand-500/50 hover:shadow-md dark:hover:shadow-black/40 transition-all duration-200 flex flex-col justify-between"
      >
        <div class="flex items-start gap-3.5">
          <div class="w-10 h-10 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center justify-center shrink-0 group-hover:scale-105 group-hover:bg-brand-500/20 transition-all">
            <Sliders class="w-5 h-5" />
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="text-sm font-semibold text-primary truncate group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
              {{ item.title }}
            </h3>
            <span class="inline-block font-mono text-[11px] text-muted truncate mt-0.5">
              /r/{{ item.key }}
            </span>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-border-default/60 flex items-center justify-between text-xs text-secondary">
          <span class="font-medium text-[11px] text-muted">Manage Registry</span>
          <ArrowRight class="w-3.5 h-3.5 text-muted group-hover:text-brand-500 group-hover:translate-x-1 transition-all" />
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Sliders,
  Search,
  ArrowRight,
  AlertCircle,
} from 'lucide-vue-next'

import api from '../api'
import PageHeader from '../layouts/PageHeader.vue'
import Input from '../components/ui/Input.vue'
import Button from '../components/ui/Button.vue'

const items = ref([])
const loading = ref(true)
const error = ref(null)
const q = ref('')

async function fetchConfig() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get('meta/')
    const configGroup = res.data?.groups?.Configuration || []
    items.value = configGroup
  } catch (e) {
    error.value = e.message || 'Could not fetch metadata'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchConfig()
})

const shown = computed(() => {
  if (!items.value) return []
  if (!q.value.trim()) return items.value
  const query = q.value.toLowerCase().trim()
  return items.value.filter(i =>
    (i.title && i.title.toLowerCase().includes(query)) ||
    (i.key && i.key.toLowerCase().includes(query))
  )
})
</script>
