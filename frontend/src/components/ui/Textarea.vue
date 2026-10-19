<template>
  <div class="relative w-full">
    <textarea
      :id="textareaId"
      ref="textareaRef"
      :name="name"
      :value="modelValue ?? ''"
      :disabled="disabled"
      :readonly="readonly"
      :placeholder="placeholder"
      :rows="rows"
      :maxlength="maxlength"
      :aria-invalid="invalid || fieldCtx?.invalid?.value"
      :aria-describedby="ariaDescribedby || fieldCtx?.describedBy?.value"
      :class="cn(
        'w-full bg-surface text-primary border rounded-md p-3 text-sm transition placeholder:text-muted focus-ring resize-y',
        (invalid || fieldCtx?.invalid?.value)
          ? 'border-danger-500 focus:border-danger-500 ring-2 ring-danger-500/20'
          : 'border-border-strong hover:border-slate-400 dark:hover:border-slate-500 focus:border-primary-500',
        disabled && 'opacity-60 cursor-not-allowed bg-muted pointer-events-none',
        readonly && 'bg-subtle cursor-default',
        $attrs.class
      )"
      @input="handleInput"
      @focus="$emit('focus', $event)"
      @blur="$emit('blur', $event)"
    />

    <!-- Optional character counter -->
    <div
      v-if="maxlength"
      class="text-[11px] text-muted text-right mt-1 tabular-nums"
    >
      {{ (modelValue || '').length }} / {{ maxlength }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, watch, nextTick } from 'vue'
import { cn } from '../../utils/cn'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  id: {
    type: String,
    default: '',
  },
  name: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  rows: {
    type: [Number, String],
    default: 3,
  },
  maxRows: {
    type: [Number, String],
    default: 10,
  },
  maxlength: {
    type: [Number, String],
    default: undefined,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  invalid: {
    type: Boolean,
    default: false,
  },
  autoGrow: {
    type: Boolean,
    default: true,
  },
  ariaDescribedby: {
    type: String,
    default: undefined,
  },
})

const emit = defineEmits(['update:modelValue', 'input', 'blur', 'focus'])

const fieldCtx = inject('formField', null)
const textareaId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)
const textareaRef = ref(null)

function adjustHeight() {
  if (!props.autoGrow || !textareaRef.value) return
  const el = textareaRef.value
  el.style.height = 'auto'
  const maxHeight = Number(props.maxRows) * 24
  el.style.height = Math.min(el.scrollHeight, maxHeight) + 'px'
}

function handleInput(e) {
  emit('update:modelValue', e.target.value)
  emit('input', e)
  adjustHeight()
}

watch(() => props.modelValue, () => {
  nextTick(adjustHeight)
})

onMounted(() => {
  nextTick(adjustHeight)
})
</script>
