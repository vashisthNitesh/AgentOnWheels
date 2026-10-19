<template>
  <!-- Status -->
  <StatusCell
    v-if="isStatus"
    :row="row"
    :name="name"
    :field="field"
    :value="row[name]"
  />

  <!-- Money -->
  <MoneyCell
    v-else-if="isMoney"
    :row="row"
    :name="name"
    :field="field"
    :value="row[name]"
  />

  <!-- Date / Datetime -->
  <DateCell
    v-else-if="isDate"
    :row="row"
    :name="name"
    :field="field"
    :value="row[name]"
  />

  <!-- ID / Number / Reference -->
  <IdCell
    v-else-if="isId"
    :row="row"
    :name="name"
    :field="field"
    :value="row[name]"
  />

  <!-- Weight (tonnes) -->
  <WeightCell
    v-else-if="isWeight"
    :row="row"
    :name="name"
    :field="field"
    :value="row[name]"
  />

  <!-- Distance (km) -->
  <DistanceCell
    v-else-if="isDistance"
    :row="row"
    :name="name"
    :field="field"
    :value="row[name]"
  />

  <!-- Entity (Driver, Customer, Vendor, Vehicle) -->
  <EntityCell
    v-else-if="isEntity"
    :row="row"
    :name="name"
    :field="field"
    :value="row[name]"
  />

  <!-- Boolean -->
  <BooleanCell
    v-else-if="isBoolean"
    :row="row"
    :name="name"
    :field="field"
    :value="row[name]"
  />

  <!-- Tags / Multiple Choices -->
  <TagsCell
    v-else-if="isTags"
    :row="row"
    :name="name"
    :field="field"
    :value="row[name]"
  />

  <!-- Default Text with label resolution and fallback -->
  <span
    v-else
    :class="[
      'block truncate',
      displayValue === '—' ? 'text-slate-400 dark:text-slate-600' : 'text-slate-800 dark:text-slate-200'
    ]"
    :title="displayValue !== '—' ? String(displayValue) : undefined"
  >
    {{ displayValue }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import StatusCell from './StatusCell.vue'
import MoneyCell from './MoneyCell.vue'
import DateCell from './DateCell.vue'
import IdCell from './IdCell.vue'
import WeightCell from './WeightCell.vue'
import DistanceCell from './DistanceCell.vue'
import EntityCell from './EntityCell.vue'
import BooleanCell from './BooleanCell.vue'
import TagsCell from './TagsCell.vue'

const props = defineProps({
  row: {
    type: Object,
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
  field: {
    type: Object,
    default: () => ({}),
  },
  resourceKey: String,
})

const isStatus = computed(() => {
  if (props.name === 'status' || props.name.endsWith('_status')) return true
  if (props.field?.type === 'choice' && props.name.includes('status')) return true
  return false
})

const isMoney = computed(() => {
  if (props.field?.money) return true
  const moneyNames = ['sell_rate', 'buy_rate', 'rate', 'total', 'amount', 'base_amount', 'tax_amount', 'cost', 'margin']
  return moneyNames.includes(props.name)
})

const isDate = computed(() => {
  if (props.field?.type === 'date' || props.field?.type === 'datetime') return true
  if (props.name.endsWith('_at') || props.name.endsWith('_date') || props.name === 'date') return true
  return false
})

const isId = computed(() => {
  if (props.name === 'id' || props.name === 'number' || props.name === 'code' || props.name === 'reference') return true
  if (props.name.endsWith('_ref')) return true
  return false
})

const isWeight = computed(() => {
  return props.name.endsWith('_t') || props.name === 'weight_t' || props.name === 'payload_t'
})

const isDistance = computed(() => {
  return props.name.endsWith('_km') || props.name === 'distance_km' || props.name === 'actual_km' || props.name === 'odometer_km'
})

const isEntity = computed(() => {
  const entityNames = ['customer', 'driver', 'vendor', 'vehicle', 'technician']
  if (entityNames.includes(props.name)) return true
  if (['customers', 'drivers', 'vendors', 'vehicles'].includes(props.field?.resource)) return true
  return false
})

const isBoolean = computed(() => {
  return props.field?.type === 'bool' || typeof props.row?.[props.name] === 'boolean'
})

const isTags = computed(() => {
  return props.field?.type === 'm2m' || Array.isArray(props.row?.[`${props.name}_label`])
})

const displayValue = computed(() => {
  if (props.row?.[`${props.name}_label`] !== undefined) {
    const l = props.row[`${props.name}_label`]
    return Array.isArray(l) ? l.join(', ') : (l || '—')
  }
  const v = props.row?.[props.name]
  if (v === null || v === undefined || v === '') return '—'
  return v
})
</script>
