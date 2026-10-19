<template>
  <div
    v-if="errorList.length > 0 || nonFieldError"
    class="p-4 rounded-xl border border-rose-200 dark:border-rose-900/60 bg-rose-50/80 dark:bg-rose-950/40 text-rose-900 dark:text-rose-200 shadow-xs space-y-2 select-none"
    role="alert"
    aria-live="assertive"
  >
    <div class="flex items-center gap-2 font-semibold text-xs text-rose-800 dark:text-rose-300">
      <AlertCircle class="w-4 h-4 text-rose-600 dark:text-rose-400 flex-shrink-0" />
      <span>
        {{ errorList.length }} field{{ errorList.length === 1 ? '' : 's' }} need{{ errorList.length === 1 ? 's' : '' }} attention
      </span>
    </div>

    <!-- Non-field error message if present -->
    <p v-if="nonFieldError" class="text-xs text-rose-700 dark:text-rose-300 font-medium">
      {{ nonFieldError }}
    </p>

    <!-- List of field errors with scroll-to anchors -->
    <ul v-if="errorList.length > 0" class="space-y-1 text-xs pl-6 list-disc">
      <li v-for="err in errorList" :key="err.field">
        <button
          type="button"
          class="font-medium text-rose-700 dark:text-rose-300 hover:text-rose-900 dark:hover:text-white underline text-left cursor-pointer"
          @click="scrollToField(err.field)"
        >
          <span class="font-semibold">{{ err.label }}:</span> {{ err.message }}
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { AlertCircle } from 'lucide-vue-next'

const props = defineProps({
  errors: {
    type: Object,
    default: () => ({}),
  },
  fields: {
    type: Object,
    default: () => ({}),
  },
})

const nonFieldError = computed(() => {
  return props.errors.non_field_errors || props.errors.detail || null
})

const errorList = computed(() => {
  const list = []
  for (const [k, msg] of Object.entries(props.errors)) {
    if (k === 'non_field_errors' || k === 'detail') continue
    if (!msg) continue
    const label = props.fields[k]?.label || k.replace(/_/g, ' ')
    list.push({
      field: k,
      label,
      message: Array.isArray(msg) ? msg.join(', ') : String(msg),
    })
  }
  return list
})

function scrollToField(fieldName) {
  const el = document.getElementById(`field-${fieldName}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    const input = el.querySelector('input, select, textarea, button') || el
    input.focus?.()
  }
}
</script>
