<template>
  <div :class="cn('flex flex-col gap-1.5 w-full', $attrs.class)">
    <!-- Label Row -->
    <div v-if="label || $slots.label || optional" class="flex items-center justify-between">
      <label
        v-if="label || $slots.label"
        :for="fieldId"
        class="text-xs font-medium text-primary select-none flex items-center gap-1"
      >
        <slot name="label">{{ label }}</slot>
        <span v-if="required" class="text-danger-500 font-semibold" aria-hidden="true">*</span>
      </label>
      <span v-if="optional && !required" class="text-[11px] text-muted select-none">Optional</span>
    </div>

    <!-- Input Control Slot -->
    <div class="w-full">
      <slot
        :id="fieldId"
        :aria-describedby="describedBy"
        :aria-invalid="!!error"
        :invalid="!!error"
      />
    </div>

    <!-- Error or Hint Row -->
    <p
      v-if="error"
      :id="errorId"
      role="alert"
      class="text-xs text-danger-600 dark:text-danger-400 flex items-center gap-1 mt-0.5 animate-in fade-in duration-150"
    >
      <AlertCircle class="w-3.5 h-3.5 shrink-0" />
      <span>{{ error }}</span>
    </p>
    <p
      v-else-if="hint || $slots.hint"
      :id="hintId"
      class="text-xs text-secondary mt-0.5"
    >
      <slot name="hint">{{ hint }}</slot>
    </p>
  </div>
</template>

<script setup>
import { computed, provide, ref } from 'vue'
import { AlertCircle } from 'lucide-vue-next'
import { cn } from '../../utils/cn'

let idCounter = 0

const props = defineProps({
  id: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  hint: {
    type: String,
    default: '',
  },
  error: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
  optional: {
    type: Boolean,
    default: false,
  },
})

const autoId = `aow-field-${++idCounter}`
const fieldId = computed(() => props.id || autoId)
const errorId = computed(() => `${fieldId.value}-error`)
const hintId = computed(() => `${fieldId.value}-hint`)

const describedBy = computed(() => {
  if (props.error) return errorId.value
  if (props.hint) return hintId.value
  return undefined
})

provide('formField', {
  fieldId,
  errorId,
  hintId,
  describedBy,
  invalid: computed(() => !!props.error),
})
</script>
