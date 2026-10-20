<template>
  <label
    :class="cn(
      'inline-flex items-center gap-3 cursor-pointer select-none',
      (label || description || $slots.default) && 'flex w-full justify-between',
      disabled && 'opacity-60 cursor-not-allowed pointer-events-none',
      $attrs.class
    )"
  >
    <div v-if="label || description || $slots.default" class="flex min-w-0 flex-col">
      <span class="text-sm font-medium text-primary">
        <slot>{{ label }}</slot>
      </span>
      <span v-if="description" class="text-xs text-secondary">
        {{ description }}
      </span>
    </div>

    <!-- reka-ui v2 uses modelValue / update:modelValue (the old `checked` API was ignored). -->
    <SwitchRoot
      :id="switchId"
      :model-value="!!modelValue"
      :disabled="disabled"
      :class="cn(
        'relative inline-flex h-5 w-9 shrink-0 items-center rounded-full border border-transparent transition-colors focus-ring',
        modelValue ? 'bg-primary-600 dark:bg-primary-500' : 'bg-slate-300 dark:bg-slate-600'
      )"
      @update:model-value="$emit('update:modelValue', $event)"
    >
      <SwitchThumb
        :class="cn(
          'pointer-events-none block h-4 w-4 rounded-full bg-white shadow-sm ring-0 transition-transform duration-150',
          modelValue ? 'translate-x-[17px]' : 'translate-x-[1px]'
        )"
      />
    </SwitchRoot>
  </label>
</template>

<script setup>
import { computed, inject } from 'vue'
import { SwitchRoot, SwitchThumb } from 'reka-ui'
import { cn } from '../../utils/cn'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: '',
  },
  description: {
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
})

defineEmits(['update:modelValue'])

const fieldCtx = inject('formField', null)
const switchId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)
</script>
