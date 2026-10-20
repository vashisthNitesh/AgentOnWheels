<template>
  <div :class="cn('flex w-full min-w-0 flex-col gap-1.5', $attrs.class)">
    <div v-if="label || $slots.label || optional" class="flex items-baseline justify-between gap-2">
      <label
        v-if="label || $slots.label"
        :for="fieldId"
        class="flex items-center gap-1 text-[13px] font-medium text-primary select-none"
      >
        <slot name="label">{{ label }}</slot>
        <span v-if="required" class="text-danger-500" aria-hidden="true">*</span>
      </label>
      <span v-if="optional && !required" class="text-[11px] text-muted select-none">Optional</span>
    </div>

    <div class="w-full">
      <slot
        :id="fieldId"
        :aria-describedby="describedBy"
        :aria-invalid="!!error"
        :invalid="!!error"
      />
    </div>

    <p
      v-if="error"
      :id="errorId"
      role="alert"
      class="flex items-start gap-1 text-xs text-danger-600 animate-in fade-in-0 slide-in-from-top-2 dark:text-danger-500"
    >
      <AlertCircle class="mt-px h-3.5 w-3.5 shrink-0" />
      <span>{{ error }}</span>
    </p>
    <p
      v-else-if="hint || $slots.hint"
      :id="hintId"
      class="text-xs text-muted"
    >
      <slot name="hint">{{ hint }}</slot>
    </p>
  </div>
</template>

<script setup>
import { computed, provide } from 'vue'
import { AlertCircle } from 'lucide-vue-next'
import { cn } from '../../utils/cn'

defineOptions({ inheritAttrs: false })

let idCounter = 0

const props = defineProps({
  id: { type: String, default: '' },
  label: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  required: { type: Boolean, default: false },
  optional: { type: Boolean, default: false },
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
