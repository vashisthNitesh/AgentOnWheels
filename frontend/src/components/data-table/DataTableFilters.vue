<template>
  <Drawer
    :open="open"
    title="Filters"
    description="Narrow down the records shown in this list."
    width="sm"
    @update:open="$emit('update:open', $event)"
  >
    <div class="space-y-6">
      <section v-if="meta?.status_choices?.length" class="space-y-2">
        <h3 class="section-title">Status</h3>
        <Select
          v-model="draftFilters[meta.status || 'status']"
          placeholder="All statuses"
          :options="statusOptions"
        />
      </section>

      <section v-if="meta?.dates?.length" class="space-y-3">
        <h3 class="section-title">Dates</h3>
        <FormField v-for="d in meta.dates" :key="d.name" :label="d.label">
          <DateRangePicker
            :model-value="{ from: draftDates[`${d.name}_from`] || '', to: draftDates[`${d.name}_to`] || '' }"
            placeholder="Any date"
            @update:model-value="onDateRangeChange(d.name, $event)"
          />
        </FormField>
      </section>

      <section v-if="meta?.filters?.length" class="space-y-3">
        <h3 class="section-title">Fields</h3>
        <template v-for="f in meta.filters" :key="f.name">
          <FormField v-if="f.type === 'fk'" :label="f.label">
            <Combobox
              v-model="draftFilters[f.name]"
              :options="fkOptions[f.resource] || []"
              :loading="fkLoading[f.resource]"
              :placeholder="`Any ${f.label.toLowerCase()}`"
              :search-placeholder="`Search ${pluralize(f.label)}…`"
            />
          </FormField>

          <FormField v-else-if="f.type === 'choice'" :label="f.label">
            <Select
              v-model="draftFilters[f.name]"
              :options="getChoiceOptions(f)"
              :placeholder="`Any ${f.label.toLowerCase()}`"
            />
          </FormField>

          <FormField v-else-if="f.type === 'bool'" :label="f.label">
            <div class="grid grid-cols-3 gap-1 rounded-lg bg-muted p-1">
              <button
                v-for="opt in boolOptions"
                :key="String(opt.value)"
                type="button"
                :class="[
                  'h-7 rounded-md text-xs font-medium transition-colors',
                  String(draftFilters[f.name] ?? '') === String(opt.value ?? '')
                    ? 'bg-surface text-primary shadow-sm'
                    : 'text-muted hover:text-primary'
                ]"
                @click="draftFilters[f.name] = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </FormField>
        </template>
      </section>

      <p
        v-if="!meta?.status_choices?.length && !meta?.dates?.length && !meta?.filters?.length"
        class="py-10 text-center text-sm text-muted"
      >
        This list has no additional filters.
      </p>
    </div>

    <template #footer>
      <div class="flex w-full items-center justify-between gap-2">
        <Button variant="ghost" size="sm" :disabled="draftActiveCount === 0" @click="resetDraft">
          Reset
        </Button>
        <div class="flex items-center gap-2">
          <Button variant="outline" size="sm" @click="$emit('update:open', false)">Cancel</Button>
          <Button variant="primary" size="sm" @click="applyFilters">
            Apply
            <span v-if="draftActiveCount > 0" class="rounded-full bg-white/25 px-1.5 text-[11px] leading-[18px]">
              {{ draftActiveCount }}
            </span>
          </Button>
        </div>
      </div>
    </template>
  </Drawer>
</template>

<style scoped>
.section-title {
  @apply text-[11px] font-semibold uppercase tracking-wider text-muted;
}
</style>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import Drawer from '../ui/Drawer.vue'
import Button from '../ui/Button.vue'
import Select from '../ui/Select.vue'
import Combobox from '../ui/Combobox.vue'
import DateRangePicker from '../ui/DateRangePicker.vue'
import FormField from '../ui/FormField.vue'
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

const boolOptions = [
  { value: undefined, label: 'Any' },
  { value: 'true', label: 'Yes' },
  { value: 'false', label: 'No' },
]

function getChoiceOptions(f) {
  const choices = f.choices || []
  return [{ value: undefined, label: `All ${pluralize(f.label)}` }, ...choices]
}

function pluralize(label) {
  if (!label) return 'records'
  const l = label.toLowerCase()
  if (/[^aeiou]y$/.test(l)) return l.slice(0, -1) + 'ies'
  if (/(s|x|z|ch|sh)$/.test(l)) return l + 'es'
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
  // A date range (from + to) counts as a single filter.
  const ranges = new Set()
  for (const [k, v] of Object.entries(draftDates)) {
    if (v) ranges.add(k.replace(/_(from|to)$/, ''))
  }
  count += ranges.size
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
