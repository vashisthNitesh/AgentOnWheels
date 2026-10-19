<template>
  <label
    :class="cn(
      'flex items-center justify-between gap-3 cursor-pointer select-none',
      disabled && 'opacity-60 cursor-not-allowed pointer-events-none',
      $attrs.class
    )"
  >
    <div v-if="label || description || $slots.default" class="flex flex-col">
      <span class="text-xs font-medium text-primary">
        <slot>{{ label }}</slot>
      </span>
      <span v-if="description" class="text-[11px] text-secondary">
        {{ description }}
      </span>
    </div>

    <SwitchRoot
      :id="switchId"
      :checked="modelValue"
      :disabled="disabled"
      :class="cn(
        'w-9 h-5 rounded-full relative transition-colors focus-ring shrink-0',
        modelValue ? 'bg-primary-600 dark:bg-primary-500' : 'bg-muted border border-border-strong'
      )"
      @update:checked="$emit('update:modelValue', $event)"
    >
      <SwitchThumb
        :class="cn(
          'block w-4 h-4 rounded-full bg-white shadow-xs transition-transform duration-150',
          modelValue ? 'translate-x-[18px]' : 'translate-x-0.5'
        )"
      />
    </SwitchRoot>
  </label>
</template>

<script setup>
import { computed, inject } from 'vue'
import { SwitchRoot, SwitchThumb } from 'reka-ui'
import { cn } from '../../utils/cn'

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
