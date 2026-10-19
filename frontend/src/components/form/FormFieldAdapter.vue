<template>
  <FormField
    :id="`field-${name}`"
    :label="field.label || formatLabel(name)"
    :required="field.required"
    :optional="!field.required && !field.readonly"
    :hint="field.help"
    :error="error"
  >
    <!-- Readonly Field Display -->
    <div
      v-if="field.readonly"
      class="h-9 px-3 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-600 dark:text-slate-400 flex items-center"
    >
      {{ modelValue ?? '—' }}
    </div>

    <!-- Boolean Switch -->
    <div v-else-if="field.type === 'bool'" class="pt-1.5 flex items-center justify-between">
      <span class="text-xs text-slate-500 dark:text-slate-400">{{ field.help || 'Enable or disable this option' }}</span>
      <Switch
        :model-value="!!modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
      />
    </div>

    <!-- Long Textarea -->
    <Textarea
      v-else-if="isLongText"
      :id="`field-${name}`"
      :model-value="modelValue ?? ''"
      :rows="3"
      :placeholder="`Enter ${field.label?.toLowerCase() || 'details'}…`"
      :error="!!error"
      @update:model-value="$emit('update:modelValue', $event)"
      @blur="$emit('blur')"
    />

    <!-- Foreign Key: Async Combobox -->
    <Combobox
      v-else-if="field.type === 'fk'"
      :id="`field-${name}`"
      :model-value="modelValue"
      :options="fkOptions"
      :loading="fkLoading"
      :placeholder="`Select ${field.label?.toLowerCase()}…`"
      :error="!!error"
      @update:model-value="onFkChange"
      @blur="$emit('blur')"
    />

    <!-- M2M: MultiSelect -->
    <MultiSelect
      v-else-if="field.type === 'm2m'"
      :id="`field-${name}`"
      :model-value="Array.isArray(modelValue) ? modelValue : []"
      :options="fkOptions"
      :loading="fkLoading"
      :placeholder="`Select ${field.label?.toLowerCase()}…`"
      :error="!!error"
      @update:model-value="$emit('update:modelValue', $event)"
      @blur="$emit('blur')"
    />

    <!-- Choice Select / RadioGroup -->
    <Select
      v-else-if="field.type === 'choice'"
      :id="`field-${name}`"
      :model-value="modelValue"
      :options="field.choices || []"
      :placeholder="`Select ${field.label?.toLowerCase()}…`"
      :error="!!error"
      @update:model-value="$emit('update:modelValue', $event)"
      @blur="$emit('blur')"
    />

    <!-- Date / Datetime Picker -->
    <DatePicker
      v-else-if="field.type === 'date' || field.type === 'datetime'"
      :id="`field-${name}`"
      :model-value="modelValue"
      :include-time="field.type === 'datetime'"
      :placeholder="`Select ${field.label?.toLowerCase()}…`"
      :error="!!error"
      @update:model-value="$emit('update:modelValue', $event)"
      @blur="$emit('blur')"
    />

    <!-- Money Currency Input -->
    <Input
      v-else-if="field.money"
      :id="`field-${name}`"
      :model-value="modelValue"
      type="number"
      step="0.01"
      :prefix="currencyPrefix"
      placeholder="0.00"
      :error="!!error"
      @update:model-value="$emit('update:modelValue', $event === '' ? null : $event)"
      @blur="$emit('blur')"
    />

    <!-- Numeric Input with Unit Suffix -->
    <Input
      v-else-if="unitSuffix"
      :id="`field-${name}`"
      :model-value="modelValue"
      type="number"
      :step="field.type === 'decimal' || field.type === 'float' ? '0.01' : '1'"
      :suffix="unitSuffix"
      placeholder="0.00"
      :error="!!error"
      @update:model-value="$emit('update:modelValue', $event === '' ? null : $event)"
      @blur="$emit('blur')"
    />

    <!-- Standard Text / Number / Email Input -->
    <Input
      v-else
      :id="`field-${name}`"
      :model-value="modelValue"
      :type="inputType"
      :placeholder="`Enter ${field.label?.toLowerCase() || name}…`"
      :error="!!error"
      @update:model-value="$emit('update:modelValue', $event === '' ? null : $event)"
      @blur="$emit('blur')"
    />
  </FormField>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import FormField from '../ui/FormField.vue'
import Input from '../ui/Input.vue'
import Textarea from '../ui/Textarea.vue'
import Select from '../ui/Select.vue'
import Combobox from '../ui/Combobox.vue'
import MultiSelect from '../ui/MultiSelect.vue'
import DatePicker from '../ui/DatePicker.vue'
import Switch from '../ui/Switch.vue'
import api from '../../api'

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  field: {
    type: Object,
    required: true,
  },
  modelValue: [String, Number, Boolean, Array, Object],
  error: String,
  currency: {
    type: String,
    default: 'AED',
  },
  initialLabel: String,
})

const emit = defineEmits(['update:modelValue', 'blur', 'fk-select'])

const isLongText = computed(() => {
  return props.field.type === 'text' || props.name === 'notes' || props.name === 'remarks' || props.name.includes('address')
})

const unitSuffix = computed(() => {
  if (props.name.endsWith('_t') || props.name === 'weight_t' || props.name === 'payload_t') return 't'
  if (props.name.endsWith('_km') || props.name === 'distance_km' || props.name === 'odometer_km') return 'km'
  if (props.name.endsWith('_pct') || props.name.includes('rate_pct')) return '%'
  if (props.name.endsWith('_cm')) return 'cm'
  if (props.name.endsWith('_mm')) return 'mm'
  if (props.name === 'days' || props.name.endsWith('_days')) return 'days'
  return null
})

const currencyPrefix = computed(() => {
  return props.currency || 'AED'
})

const inputType = computed(() => {
  if (['int', 'float', 'decimal'].includes(props.field.type)) return 'number'
  if (props.field.type === 'email' || props.name.includes('email')) return 'email'
  if (props.name.includes('phone')) return 'tel'
  return 'text'
})

function formatLabel(name) {
  return name.replace(/_/g, ' ').replace(/^./, (s) => s.toUpperCase())
}

// FK Options Loading
const fkOptions = ref([])
const fkLoading = ref(false)
const cache = (window.__refCache ||= {})

async function loadFkOptions() {
  const resource = props.field.resource
  if (!resource) return

  // Preserve initial label on edit
  if (props.modelValue && props.initialLabel && !fkOptions.value.some((o) => o.value === props.modelValue)) {
    fkOptions.value.push({ value: props.modelValue, label: props.initialLabel })
  }

  fkLoading.value = true
  try {
    if (!cache[resource]) {
      cache[resource] = api.get(`${resource}/`, { params: { page_size: 500 } }).then((r) => r.data.results)
    }
    const results = await cache[resource]
    fkOptions.value = (results || []).map((item) => ({
      value: item.id,
      label: item.display || item.company_name || item.name || item.plate_number || `#${item.id}`,
      raw: item,
    }))
  } catch (e) {
    console.warn(`Failed loading FK ${resource}`, e)
  } finally {
    fkLoading.value = false
  }
}

function onFkChange(val) {
  emit('update:modelValue', val)
  const selectedOpt = fkOptions.value.find((o) => o.value === val)
  emit('fk-select', { name: props.name, value: val, option: selectedOpt })
}

watch(
  () => props.field.resource,
  (res) => {
    if (res) loadFkOptions()
  }
)

onMounted(() => {
  if (props.field.type === 'fk' || props.field.type === 'm2m') {
    loadFkOptions()
  }
})
</script>
