<template>
  <nav aria-label="Progress" class="w-full max-w-full">
    <ol :class="cn('flex items-center gap-1.5 sm:gap-3 overflow-x-auto scrollbar-none py-2 px-0.5 max-w-full touch-pan-x', $attrs.class)">
      <li
        v-for="(step, idx) in steps"
        :key="idx"
        class="flex items-center gap-1.5 sm:gap-3 shrink-0"
      >
        <!-- Step Button / Indicator -->
        <button
          type="button"
          :disabled="!isStepClickable(idx)"
          :aria-current="idx === currentStep ? 'step' : undefined"
          :class="cn(
            'flex items-center gap-2 rounded-full py-1.5 px-3 text-xs font-medium transition-all select-none focus-ring shrink-0',
            idx === currentStep && !step.hasError && 'bg-primary-600 text-white shadow-xs dark:bg-primary-500 font-semibold',
            idx === currentStep && step.hasError && 'bg-rose-600 text-white shadow-xs dark:bg-rose-600 font-semibold ring-2 ring-rose-500/30',
            step.hasError && idx !== currentStep && 'bg-rose-100/90 text-rose-900 border border-rose-300 dark:bg-rose-950/70 dark:text-rose-200 dark:border-rose-800 font-medium',
            idx < currentStep && !step.hasError && 'bg-subtle text-secondary hover:text-primary hover:bg-muted border border-border-default',
            idx > currentStep && !step.hasError && 'text-muted bg-transparent opacity-60 cursor-not-allowed',
            isStepClickable(idx) && 'cursor-pointer'
          )"
          @click="onStepClick(idx)"
        >
          <!-- Step Index, Error, or Check icon -->
          <span
            :class="cn(
              'flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold shrink-0',
              step.hasError
                ? 'bg-rose-600 text-white dark:bg-rose-500 dark:text-white shadow-xs'
                : idx === currentStep
                  ? 'bg-white/20 text-white'
                  : idx < currentStep
                    ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                    : 'bg-muted text-muted'
            )"
          >
            <AlertCircle v-if="step.hasError" class="w-3.5 h-3.5 text-white stroke-[2.5]" />
            <Check v-else-if="idx < currentStep" class="w-3 h-3 stroke-[3]" />
            <span v-else>{{ idx + 1 }}</span>
          </span>

          <span class="truncate max-w-[120px] sm:max-w-none">{{ step.title || step.label }}</span>
        </button>

        <!-- Divider line between steps -->
        <div
          v-if="idx < steps.length - 1"
          :class="cn(
            'hidden sm:block h-[1px] w-4 lg:w-8 bg-border-default shrink-0',
            idx < currentStep && 'bg-primary-500/50'
          )"
        />
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { Check, AlertCircle } from 'lucide-vue-next'
import { cn } from '../../utils/cn'

const props = defineProps({
  steps: {
    type: Array,
    required: true,
  },
  currentStep: {
    type: Number,
    default: 0,
  },
  maxVisitedStep: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['update:currentStep', 'step-click'])

function isStepClickable(idx) {
  return idx <= Math.max(props.currentStep, props.maxVisitedStep)
}

function onStepClick(idx) {
  if (isStepClickable(idx)) {
    emit('update:currentStep', idx)
    emit('step-click', idx)
  }
}
</script>
