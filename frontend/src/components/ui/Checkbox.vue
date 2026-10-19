<template>
  <label
    :class="cn(
      'inline-flex items-center gap-2 cursor-pointer select-none text-xs text-primary',
      disabled && 'opacity-60 cursor-not-allowed pointer-events-none',
      $attrs.class
    )"
  >
    <CheckboxRoot
      :id="checkboxId"
      :checked="modelValue"
      :disabled="disabled"
      :aria-invalid="invalid || fieldCtx?.invalid?.value"
      :class="cn(
        'w-4 h-4 rounded border flex items-center justify-center transition-colors focus-ring',
        modelValue
          ? 'bg-primary-600 border-primary-600 text-white dark:bg-primary-500 dark:border-primary-500'
          : 'bg-surface border-border-strong hover:border-slate-400 dark:hover:border-slate-500',
        (invalid || fieldCtx?.invalid?.value) && 'border-danger-500 ring-2 ring-danger-500/20'
      )"
      @update:checked="$emit('update:modelValue', $event)"
    >
      <CheckboxIndicator class="flex items-center justify-center text-current">
        <Minus v-if="modelValue === 'indeterminate'" class="w-3 h-3 stroke-[3]" />
        <Check v-else class="w-3 h-3 stroke-[3]" />
      </CheckboxIndicator>
    </CheckboxRoot>

    <span v-if="label || $slots.default" class="font-medium">
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>

<script setup>
import { computed, inject } from 'vue'
import { CheckboxRoot, CheckboxIndicator } from 'reka-ui'
import { Check, Minus } from 'lucide-vue-next'
import { cn } from '../../utils/cn'

const props = defineProps({
  modelValue: {
    type: [Boolean, String],
    default: false,
  },
  label: {
    type: String,
    default: '',
  },
  id: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  invalid: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['update:modelValue'])

const fieldCtx = inject('formField', null)
const checkboxId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)
</script>
