<template>
  <FormField
    :id="`field-${name}`"
    :class="$attrs.class"
    :label="field.label || formatLabel(name)"
    :required="field.required"
    :optional="!field.required && !field.readonly && field.type !== 'bool'"
    :hint="field.type === 'bool' ? '' : field.help"
    :error="error"
  >
    <!-- Readonly -->
    <div
      v-if="field.readonly"
      class="flex h-9 items-center rounded-lg border border-dashed border-border-strong bg-subtle px-3 text-sm text-secondary"
    >
      {{ readonlyDisplay }}
    </div>

    <!-- Boolean -->
    <div
      v-else-if="field.type === 'bool'"
      class="flex h-9 items-center justify-between gap-3 rounded-lg border border-border-strong bg-surface px-3 shadow-xs"
    >
      <span class="truncate text-sm text-secondary">{{ field.help || (modelValue ? 'Enabled' : 'Disabled') }}</span>
      <Switch
        :id="`field-${name}`"
        :model-value="!!modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
      />
    </div>

    <!-- Long text -->
    <Textarea
      v-else-if="isLongText"
      :id="`field-${name}`"
      :model-value="modelValue ?? ''"
      :rows="3"
      :placeholder="`Enter ${lowerLabel}…`"
      @update:model-value="$emit('update:modelValue', $event)"
      @blur="$emit('blur')"
    />

    <!-- Foreign key -->
    <Combobox
      v-else-if="field.type === 'fk'"
      :id="`field-${name}`"
      :model-value="modelValue"
      :options="fkOptions"
      :loading="fkLoading"
      :placeholder="`Select ${lowerLabel}…`"
      :search-placeholder="`Search ${lowerLabel}…`"
      @update:model-value="onFkChange"
      @blur="$emit('blur')"
    />

    <!-- Many-to-many -->
    <MultiSelect
      v-else-if="field.type === 'm2m'"
      :id="`field-${name}`"
      :model-value="Array.isArray(modelValue) ? modelValue : []"
      :options="fkOptions"
      :loading="fkLoading"
      :placeholder="`Select ${lowerLabel}…`"
      @update:model-value="$emit('update:modelValue', $event)"
      @blur="$emit('blur')"
    />

    <!-- Choice -->
    <Select
      v-else-if="field.type === 'choice'"
      :id="`field-${name}`"
      :model-value="modelValue"
      :options="field.choices || []"
      :placeholder="`Select ${lowerLabel}…`"
      :clearable="!field.required"
      @update:model-value="onChoiceChange"
    />

    <!-- Date / datetime -->
    <DatePicker
      v-else-if="field.type === 'date' || field.type === 'datetime'"
      :id="`field-${name}`"
      :model-value="modelValue"
      :with-time="field.type === 'datetime'"
      :placeholder="field.type === 'datetime' ? 'Select date & time…' : 'Select date…'"
      @update:model-value="onChoiceChange"
      @blur="$emit('blur')"
    />

    <!-- Money -->
    <Input
      v-else-if="field.money"
      :id="`field-${name}`"
      :model-value="modelValue"
      type="number"
      step="0.01"
      inputmode="decimal"
      class="text-right tabular-nums"
      :prefix="currency || 'AED'"
      placeholder="0.00"
      @update:model-value="$emit('update:modelValue', $event === '' ? null : $event)"
      @blur="$emit('blur')"
    />

    <!-- Number with unit -->
    <Input
      v-else-if="unitSuffix"
      :id="`field-${name}`"
      :model-value="modelValue"
      type="number"
      :step="isDecimal ? '0.01' : '1'"
      :inputmode="isDecimal ? 'decimal' : 'numeric'"
      class="tabular-nums"
      :suffix="unitSuffix"
      :placeholder="isDecimal ? '0.00' : '0'"
      @update:model-value="$emit('update:modelValue', $event === '' ? null : $event)"
      @blur="$emit('blur')"
    />

    <!-- Plain text / number / email / phone -->
    <Input
      v-else
      :id="`field-${name}`"
      :model-value="modelValue"
      :type="inputType"
      :inputmode="inputType === 'number' ? (isDecimal ? 'decimal' : 'numeric') : undefined"
      :step="inputType === 'number' ? (isDecimal ? '0.01' : '1') : undefined"
      :class="inputType === 'number' ? 'tabular-nums' : ''"
      :autocomplete="inputType === 'email' ? 'email' : inputType === 'tel' ? 'tel' : 'off'"
      :placeholder="placeholderText"
      @update:model-value="$emit('update:modelValue', $event === '' ? null : $event)"
      @blur="$emit('blur')"
    >
      <template v-if="inputType === 'email'" #prefix><Mail class="h-4 w-4" /></template>
      <template v-else-if="inputType === 'tel'" #prefix><Phone class="h-4 w-4" /></template>
    </Input>
  </FormField>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Mail, Phone } from 'lucide-vue-next'
import FormField from '../ui/FormField.vue'
import Input from '../ui/Input.vue'
import Textarea from '../ui/Textarea.vue'
import Select from '../ui/Select.vue'
import Combobox from '../ui/Combobox.vue'
import MultiSelect from '../ui/MultiSelect.vue'
import DatePicker from '../ui/DatePicker.vue'
import Switch from '../ui/Switch.vue'
import api from '../../api'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  name: { type: String, required: true },
  field: { type: Object, required: true },
  modelValue: [String, Number, Boolean, Array, Object],
  error: String,
  currency: { type: String, default: 'AED' },
  initialLabel: String,
})

const emit = defineEmits(['update:modelValue', 'blur', 'fk-select'])

const lowerLabel = computed(() => (props.field.label || formatLabel(props.name)).toLowerCase())
const isDecimal = computed(() => ['decimal', 'float'].includes(props.field.type))

const isLongText = computed(() =>
  props.field.type === 'text' || props.name === 'notes' || props.name === 'remarks' || props.name.includes('address')
)

const unitSuffix = computed(() => {
  const n = props.name
  if (n.endsWith('_t')) return 't'
  if (n.endsWith('_km')) return 'km'
  if (n.endsWith('_pct') || n.includes('rate_pct')) return '%'
  if (n.endsWith('_cm')) return 'cm'
  if (n.endsWith('_mm')) return 'mm'
  if (n.endsWith('_kg')) return 'kg'
  if (n === 'days' || n.endsWith('_days')) return 'days'
  if (n.endsWith('_hours') || n.endsWith('_hrs')) return 'hrs'
  return null
})

const inputType = computed(() => {
  if (['int', 'float', 'decimal'].includes(props.field.type)) return 'number'
  if (props.field.type === 'email' || props.name.includes('email')) return 'email'
  if (props.name.includes('phone') || props.name.includes('mobile')) return 'tel'
  return 'text'
})

const placeholderText = computed(() => {
  if (inputType.value === 'email') return 'name@company.com'
  if (inputType.value === 'tel') return '+971 50 000 0000'
  if (inputType.value === 'number') return isDecimal.value ? '0.00' : '0'
  return `Enter ${lowerLabel.value}…`
})

const readonlyDisplay = computed(() => {
  const v = props.modelValue
  if (v === null || v === undefined || v === '') return '—'
  if (typeof v === 'boolean') return v ? 'Yes' : 'No'
  return String(v)
})

function formatLabel(name) {
  return name.replace(/_/g, ' ').replace(/^./, (s) => s.toUpperCase())
}

// Choice / date values: emit and validate immediately (no native blur event).
function onChoiceChange(val) {
  emit('update:modelValue', val)
  emit('blur')
}

// FK options (shared cache across all fields on the page)
const fkOptions = ref([])
const fkLoading = ref(false)
const cache = (window.__refCache ||= {})

async function loadFkOptions() {
  const resource = props.field.resource
  if (!resource) return
  if (props.modelValue && props.initialLabel) {
    fkOptions.value = [{ value: props.modelValue, label: props.initialLabel }]
  }
  fkLoading.value = true
  try {
    if (!cache[resource]) {
      cache[resource] = api
        .get(`${resource}/`, { params: { page_size: 500 } })
        .then((r) => r.data.results)
        .catch((e) => {
          delete cache[resource]
          throw e
        })
    }
    const results = await cache[resource]
    fkOptions.value = (results || []).map((item) => ({
      value: item.id,
      label: item.display || item.company_name || item.name || item.plate_number || item.number || `#${item.id}`,
      code: item.code || item.plate_number || undefined,
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
  const option = fkOptions.value.find((o) => o.value === val)
  emit('fk-select', { name: props.name, value: val, option })
  emit('blur')
}

watch(() => props.field.resource, (res) => res && loadFkOptions())

onMounted(() => {
  if (props.field.type === 'fk' || props.field.type === 'm2m') loadFkOptions()
})
</script>
