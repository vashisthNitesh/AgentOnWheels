<template>
  <div class="relative w-full">
    <textarea
      :id="textareaId"
      ref="textareaRef"
      v-bind="restAttrs"
      :name="name"
      :value="modelValue ?? ''"
      :disabled="disabled"
      :readonly="readonly"
      :placeholder="placeholder"
      :rows="rows"
      :maxlength="maxlength"
      :aria-invalid="isInvalid || undefined"
      :aria-describedby="ariaDescribedby || fieldCtx?.describedBy?.value"
      :class="cn(
        controlBase,
        'block rounded-lg px-3 py-2.5 text-sm leading-relaxed resize-y min-h-[84px]',
        isInvalid ? controlInvalid : controlIdle,
        disabled && controlDisabled,
        readonly && 'bg-subtle cursor-default',
        $attrs.class
      )"
      @input="handleInput"
      @focus="$emit('focus', $event)"
      @blur="$emit('blur', $event)"
    />

    <div
      v-if="maxlength"
      class="mt-1 text-right text-[11px] tabular-nums text-muted"
    >
      {{ (modelValue || '').length }} / {{ maxlength }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, watch, nextTick, useAttrs } from 'vue'
import { cn } from '../../utils/cn'
import { controlBase, controlIdle, controlInvalid, controlDisabled } from './controlStyles'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: {
    type: [String, null],
    default: '',
  },
  id: { type: String, default: '' },
  name: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  rows: { type: [Number, String], default: 3 },
  maxRows: { type: [Number, String], default: 12 },
  maxlength: { type: [Number, String], default: undefined },
  disabled: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  invalid: { type: Boolean, default: false },
  error: { type: Boolean, default: false },
  autoGrow: { type: Boolean, default: true },
  ariaDescribedby: { type: String, default: undefined },
})

const emit = defineEmits(['update:modelValue', 'input', 'blur', 'focus'])

const attrs = useAttrs()
const restAttrs = computed(() => {
  const { class: _c, ...rest } = attrs
  return rest
})

const fieldCtx = inject('formField', null)
const textareaId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)
const isInvalid = computed(() => props.invalid || props.error || !!fieldCtx?.invalid?.value)
const textareaRef = ref(null)

function adjustHeight() {
  if (!props.autoGrow || !textareaRef.value) return
  const el = textareaRef.value
  el.style.height = 'auto'
  const maxHeight = Number(props.maxRows) * 24
  el.style.height = Math.min(el.scrollHeight + 2, maxHeight) + 'px'
}

function handleInput(e) {
  emit('update:modelValue', e.target.value)
  emit('input', e)
  adjustHeight()
}

watch(() => props.modelValue, () => nextTick(adjustHeight))
onMounted(() => nextTick(adjustHeight))
</script>
