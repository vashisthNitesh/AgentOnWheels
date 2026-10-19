<template>
  <aside class="w-80 flex-shrink-0 space-y-4 sticky top-24 self-start select-none">
    <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-4">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2.5">
        <div>
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Form Summary
          </h3>
          <p class="text-[11px] text-slate-400 mt-0.5">
            {{ filledCount }} of {{ totalFieldsCount }} fields completed
          </p>
        </div>
        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-brand-50 text-brand-700 dark:bg-brand-950/50 dark:text-brand-300">
          Step {{ currentStep + 1 }}/{{ steps.length }}
        </span>
      </div>

      <!-- Step-by-Step Overview -->
      <div class="space-y-3.5 divide-y divide-slate-100 dark:divide-slate-800/60 text-xs">
        <div
          v-for="(s, idx) in steps"
          :key="idx"
          :class="['pt-3 first:pt-0 space-y-1.5', idx === currentStep && 'opacity-100', idx > currentStep && 'opacity-60']"
        >
          <div class="flex items-center justify-between">
            <span class="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <span
                :class="[
                  'h-4 w-4 rounded-full flex items-center justify-center text-[10px] font-bold',
                  isStepCompleted(idx)
                    ? 'bg-emerald-500 text-white'
                    : idx === currentStep
                      ? 'bg-brand-600 text-white'
                      : 'bg-slate-200 dark:bg-slate-800 text-slate-500'
                ]"
              >
                {{ isStepCompleted(idx) ? '✓' : idx + 1 }}
              </span>
              {{ s.title }}
            </span>

            <button
              v-if="idx !== currentStep"
              type="button"
              class="text-[11px] font-medium text-brand-600 dark:text-brand-400 hover:underline"
              @click="$emit('go-to-step', idx)"
            >
              Edit
            </button>
          </div>

          <!-- Key Values Preview for this step -->
          <ul class="space-y-1 pl-5.5 text-[11px]">
            <li
              v-for="fieldName in s.fields.slice(0, 4)"
              :key="fieldName"
              class="flex justify-between items-center text-slate-500 dark:text-slate-400"
            >
              <span class="truncate max-w-[120px]">{{ fields[fieldName]?.label || fieldName }}:</span>
              <span class="font-medium text-slate-800 dark:text-slate-200 truncate max-w-[110px] text-right">
                {{ formatValue(formData[fieldName], fields[fieldName]) }}
              </span>
            </li>
            <li v-if="s.fields.length > 4" class="text-[10px] text-slate-400 italic">
              +{{ s.fields.length - 4 }} more fields
            </li>
          </ul>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  steps: {
    type: Array,
    required: true,
  },
  currentStep: {
    type: Number,
    required: true,
  },
  formData: {
    type: Object,
    required: true,
  },
  fields: {
    type: Object,
    default: () => ({}),
  },
  errors: {
    type: Object,
    default: () => ({}),
  },
})

defineEmits(['go-to-step'])

const totalFieldsCount = computed(() => {
  return props.steps.reduce((acc, s) => acc + s.fields.length, 0)
})

const filledCount = computed(() => {
  let count = 0
  for (const s of props.steps) {
    for (const f of s.fields) {
      const v = props.formData[f]
      if (v !== undefined && v !== null && v !== '' && (!Array.isArray(v) || v.length > 0)) {
        count++
      }
    }
  }
  return count
})

function isStepCompleted(stepIdx) {
  const step = props.steps[stepIdx]
  if (!step) return false
  const hasErrors = step.fields.some((f) => !!props.errors[f])
  if (hasErrors) return false
  const requiredFields = step.fields.filter((f) => props.fields[f]?.required)
  if (requiredFields.length === 0) return true
  return requiredFields.every((f) => {
    const v = props.formData[f]
    return v !== undefined && v !== null && v !== '' && (!Array.isArray(v) || v.length > 0)
  })
}

function formatValue(val, field) {
  if (val === undefined || val === null || val === '') return '—'
  if (typeof val === 'boolean') return val ? 'Yes' : 'No'
  if (Array.isArray(val)) return `${val.length} selected`
  if (field?.money) return `${val} AED`
  return String(val)
}
</script>
