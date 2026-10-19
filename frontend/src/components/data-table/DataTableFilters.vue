<template>
  <Drawer
    :open="open"
    title="Filter Records"
    description="Refine displayed records using field filters and date ranges."
    size="md"
    @update:open="$emit('update:open', $event)"
  >
    <div class="space-y-6 py-2">
      <!-- Section: Status & State -->
      <div v-if="meta?.status_choices?.length" class="space-y-2.5">
        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Status
        </label>
        <Select
          v-model="draftFilters[meta.status || 'status']"
          placeholder="All statuses"
          :options="statusOptions"
        />
      </div>

      <!-- Section: Date Ranges -->
      <div v-if="meta?.dates?.length" class="space-y-4">
        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Date Ranges
        </label>
        <div v-for="d in meta.dates" :key="d.name" class="space-y-1.5">
          <span class="text-xs font-medium text-slate-700 dark:text-slate-300">{{ d.label }}</span>
          <DateRangePicker
            :model-value="{
              from: draftDates[`${d.name}_from`],
              to: draftDates[`${d.name}_to`]
            }"
            placeholder="Select date range"
            @update:model-value="onDateRangeChange(d.name, $event)"
          />
        </div>
      </div>

      <!-- Section: Relational & Choice Filters -->
      <div v-if="meta?.filters?.length" class="space-y-4">
        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Field Filters
        </label>
        <div class="grid grid-cols-1 gap-4">
          <template v-for="f in meta.filters" :key="f.name">
            <!-- FK Reference Filter -->
            <div v-if="f.type === 'fk'" class="space-y-1.5">
              <label class="text-xs font-medium text-slate-700 dark:text-slate-300">
                {{ f.label }}
              </label>
              <Combobox
                v-model="draftFilters[f.name]"
                :options="fkOptions[f.resource] || []"
                :loading="fkLoading[f.resource]"
                :placeholder="`All ${pluralize(f.label)}`"
              />
            </div>

            <!-- Choice Filter -->
            <div v-else-if="f.type === 'choice'" class="space-y-1.5">
              <label class="text-xs font-medium text-slate-700 dark:text-slate-300">
                {{ f.label }}
              </label>
              <Select
                v-model="draftFilters[f.name]"
                :options="getChoiceOptions(f)"
                :placeholder="`All ${pluralize(f.label)}`"
              />
            </div>

            <!-- Boolean Filter -->
            <div v-else-if="f.type === 'bool'" class="flex items-center justify-between py-1">
              <div>
                <span class="text-xs font-medium text-slate-700 dark:text-slate-300">{{ f.label }}</span>
                <p class="text-[11px] text-slate-400">Filter by positive status</p>
              </div>
              <Select
                v-model="draftFilters[f.name]"
                class="w-32"
                :options="[
                  { value: undefined, label: 'Any' },
                  { value: 'true', label: 'Yes' },
                  { value: 'false', label: 'No' },
                ]"
              />
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Drawer Sticky Footer -->
    <template #footer>
      <div class="flex items-center justify-between w-full">
        <button
          type="button"
          class="text-xs font-medium text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
          @click="resetDraft"
        >
          Reset filters
        </button>
        <div class="flex items-center gap-2">
          <Button variant="outline" size="sm" @click="$emit('update:open', false)">
            Cancel
          </Button>
          <Button variant="primary" size="sm" @click="applyFilters">
            Apply Filters
            <span v-if="draftActiveCount > 0" class="ml-1.5 px-1.5 py-0.2 rounded-full text-[10px] bg-white/20">
              {{ draftActiveCount }}
            </span>
          </Button>
        </div>
      </div>
    </template>
  </Drawer>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import Drawer from '../ui/Drawer.vue'
import Button from '../ui/Button.vue'
import Select from '../ui/Select.vue'
import Combobox from '../ui/Combobox.vue'
import DateRangePicker from '../ui/DateRangePicker.vue'
import api from '../../api'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  meta: {
    type: Object,
    default: () => ({}),
  },
  filters: {
    type: Object,
    default: () => ({}),
  },
  dates: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:open', 'apply', 'reset'])

// Local Draft State
const draftFilters = reactive({})
const draftDates = reactive({})

// FK Caching
const fkOptions = reactive({})
const fkLoading = reactive({})
const cache = (window.__refCache ||= {})

function syncFromProps() {
  // Clear draft
  Object.keys(draftFilters).forEach((k) => delete draftFilters[k])
  Object.keys(draftDates).forEach((k) => delete draftDates[k])

  // Hydrate from props
  Object.assign(draftFilters, props.filters)
  Object.assign(draftDates, props.dates)
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      syncFromProps()
      loadFkResources()
    }
  },
  { immediate: true }
)

const statusOptions = computed(() => {
  const choices = props.meta?.status_choices || []
  return [{ value: undefined, label: 'All statuses' }, ...choices.map((c) => ({ value: c.value, label: c.label }))]
})

function getChoiceOptions(f) {
  const choices = f.choices || []
  return [{ value: undefined, label: `All ${pluralize(f.label)}` }, ...choices]
}

function pluralize(label) {
  if (!label) return 'records'
  const l = label.toLowerCase()
  if (l.endsWith('y')) return l.slice(0, -1) + 'ies'
  if (l.endsWith('s') || l.endsWith('ch')) return l + 'es'
  return l + 's'
}

function onDateRangeChange(fieldName, range) {
  if (!range || (!range.from && !range.to)) {
    delete draftDates[`${fieldName}_from`]
    delete draftDates[`${fieldName}_to`]
  } else {
    draftDates[`${fieldName}_from`] = range.from || ''
    draftDates[`${fieldName}_to`] = range.to || ''
  }
}

async function loadFkResources() {
  if (!props.meta?.filters) return
  for (const f of props.meta.filters) {
    if (f.type === 'fk' && f.resource && !fkOptions[f.resource]) {
      fkLoading[f.resource] = true
      try {
        if (!cache[f.resource]) {
          cache[f.resource] = api.get(`${f.resource}/`, { params: { page_size: 500 } }).then((r) => r.data.results)
        }
        const results = await cache[f.resource]
        fkOptions[f.resource] = (results || []).map((item) => ({
          value: item.id,
          label: item.display || item.company_name || item.name || item.plate_number || `#${item.id}`,
        }))
      } catch (e) {
        console.warn(`Failed loading FK ${f.resource}`, e)
        fkOptions[f.resource] = []
      } finally {
        fkLoading[f.resource] = false
      }
    }
  }
}

const draftActiveCount = computed(() => {
  let count = 0
  for (const [k, v] of Object.entries(draftFilters)) {
    if (v !== undefined && v !== null && v !== '' && v !== 'all') count++
  }
  for (const [k, v] of Object.entries(draftDates)) {
    if (v) count++
  }
  return count
})

function resetDraft() {
  Object.keys(draftFilters).forEach((k) => delete draftFilters[k])
  Object.keys(draftDates).forEach((k) => delete draftDates[k])
}

function applyFilters() {
  emit('apply', {
    filters: { ...draftFilters },
    dates: { ...draftDates },
  })
  emit('update:open', false)
}
</script>
