<template>
  <nav aria-label="Progress" class="w-full">
    <ol :class="cn('flex items-center gap-2 sm:gap-4 overflow-x-auto py-2', $attrs.class)">
      <li
        v-for="(step, idx) in steps"
        :key="idx"
        class="flex items-center gap-2 sm:gap-3 shrink-0"
      >
        <!-- Step Button / Indicator -->
        <button
          type="button"
          :disabled="!isStepClickable(idx)"
          :class="cn(
            'flex items-center gap-2 rounded-full py-1 px-3 text-xs font-medium transition-all select-none focus-ring',
            idx === currentStep && 'bg-primary-600 text-white shadow-xs dark:bg-primary-500 font-semibold',
            step.hasError && idx !== currentStep && 'bg-danger-50 text-danger-700 border border-danger-300 dark:bg-danger-950/40 dark:text-danger-300',
            idx < currentStep && !step.hasError && 'bg-subtle text-secondary hover:text-primary hover:bg-muted border border-border-default',
            idx > currentStep && !step.hasError && 'text-muted bg-transparent opacity-60 cursor-not-allowed',
            isStepClickable(idx) && 'cursor-pointer'
          )"
          @click="onStepClick(idx)"
        >
          <!-- Step Index or Check icon -->
          <span
            :class="cn(
              'flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold shrink-0',
              idx === currentStep ? 'bg-white/20 text-white' : idx < currentStep ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-muted text-muted'
            )"
          >
            <Check v-if="idx < currentStep && !step.hasError" class="w-3 h-3 stroke-[3]" />
            <AlertCircle v-else-if="step.hasError" class="w-3 h-3 text-danger-600 dark:text-danger-400" />
            <span v-else>{{ idx + 1 }}</span>
          </span>

          <span class="truncate">{{ step.title || step.label }}</span>
        </button>

        <!-- Divider line between steps -->
        <div
          v-if="idx < steps.length - 1"
          :class="cn(
            'hidden sm:block h-[1px] w-6 lg:w-10 bg-border-default shrink-0',
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
