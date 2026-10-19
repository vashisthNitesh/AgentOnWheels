<template>
  <RadioGroupRoot
    :model-value="modelValue !== null && modelValue !== undefined ? String(modelValue) : undefined"
    :orientation="orientation"
    :disabled="disabled"
    :class="cn(
      'flex',
      orientation === 'horizontal' ? 'flex-row flex-wrap gap-3' : 'flex-col gap-2',
      $attrs.class
    )"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div
      v-for="opt in options"
      :key="opt.value"
      :class="cn(
        'relative flex items-start gap-3 rounded-lg border transition-all cursor-pointer select-none',
        cardStyle ? 'p-3.5 bg-surface' : 'p-1 bg-transparent border-transparent',
        cardStyle && String(modelValue) === String(opt.value)
          ? 'border-primary-500 bg-primary-50/30 dark:bg-primary-950/20 shadow-xs ring-1 ring-primary-500'
          : cardStyle ? 'border-border-default hover:border-border-strong hover:bg-subtle' : '',
        disabled && 'opacity-60 cursor-not-allowed pointer-events-none'
      )"
      @click="$emit('update:modelValue', opt.value)"
    >
      <RadioGroupItem
        :id="`radio-${opt.value}`"
        :value="String(opt.value)"
        :disabled="opt.disabled || disabled"
        :class="cn(
          'w-4 h-4 rounded-full border border-border-strong bg-surface flex items-center justify-center transition-colors focus-ring mt-0.5',
          String(modelValue) === String(opt.value) && 'border-primary-600 dark:border-primary-500'
        )"
      >
        <RadioGroupIndicator class="w-2 h-2 rounded-full bg-primary-600 dark:bg-primary-500" />
      </RadioGroupItem>

      <div class="flex flex-col">
        <label :for="`radio-${opt.value}`" class="text-xs font-medium text-primary cursor-pointer">
          {{ opt.label }}
        </label>
        <span v-if="opt.description" class="text-[11px] text-secondary mt-0.5">
          {{ opt.description }}
        </span>
      </div>
    </div>
  </RadioGroupRoot>
</template>

<script setup>
import { RadioGroupRoot, RadioGroupItem, RadioGroupIndicator } from 'reka-ui'
import { cn } from '../../utils/cn'

defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null,
  },
  options: {
    type: Array,
    default: () => [],
  },
  orientation: {
    type: String,
    default: 'vertical',
    validator: v => ['horizontal', 'vertical'].includes(v),
  },
  cardStyle: {
    type: Boolean,
    default: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['update:modelValue'])
</script>
