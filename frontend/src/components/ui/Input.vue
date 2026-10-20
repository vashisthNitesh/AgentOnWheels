<template>
  <div class="w-full">
    <!--
      Input group: the wrapper owns the border and focus ring, so prefixes,
      suffixes and action buttons of any width sit inline instead of being
      absolutely positioned over the text.
    -->
    <div
      :class="cn(
        controlBase,
        'flex items-stretch overflow-hidden px-0 focus-within:border-primary-500 focus-within:ring-4 focus-within:ring-primary-500/15 dark:focus-within:ring-primary-400/20',
        wrapperSize,
        isInvalid ? controlInvalid + ' focus-within:border-danger-500 focus-within:ring-danger-500/15' : 'border-border-strong hover:border-slate-400 dark:hover:border-slate-500',
        disabled && controlDisabled,
        readonly && 'bg-subtle'
      )"
      @click="focus"
    >
      <span
        v-if="$slots.prefix || prefix"
        class="flex shrink-0 items-center pl-3 pr-1 text-muted select-none"
        :class="prefix && !$slots.prefix ? 'text-xs font-semibold tracking-wide' : ''"
      >
        <slot name="prefix">{{ prefix }}</slot>
      </span>

      <input
        :id="inputId"
        ref="inputRef"
        v-bind="inputAttrs"
        :name="name"
        :type="computedType"
        :value="modelValue ?? ''"
        :disabled="disabled"
        :readonly="readonly"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        :aria-invalid="isInvalid || undefined"
        :aria-describedby="ariaDescribedby || fieldCtx?.describedBy?.value"
        :class="cn(
          'h-full min-w-0 flex-1 bg-transparent text-primary placeholder:text-muted outline-none border-0 focus:ring-0',
          'disabled:cursor-not-allowed [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none',
          textSize,
          ($slots.prefix || prefix) ? 'pl-1.5' : padX,
          hasTrailing ? 'pr-1' : padX,
          $attrs.class
        )"
        @input="handleInput"
        @keydown="handleKeyState"
        @keyup="handleKeyState"
        @focus="$emit('focus', $event)"
        @blur="$emit('blur', $event)"
      />

      <span v-if="hasTrailing" class="flex shrink-0 items-center gap-1 pr-2.5 pl-1">
        <button
          v-if="showClear"
          type="button"
          tabindex="-1"
          class="rounded p-0.5 text-muted transition hover:bg-subtle hover:text-primary"
          aria-label="Clear input"
          @click.stop="clear"
        >
          <X class="h-3.5 w-3.5" />
        </button>

        <span
          v-if="$slots.suffix || suffix"
          class="select-none text-xs font-medium text-muted"
        >
          <slot name="suffix">{{ suffix }}</slot>
        </span>

        <button
          v-if="isPassword"
          type="button"
          tabindex="-1"
          class="rounded p-0.5 text-muted transition hover:bg-subtle hover:text-primary"
          :aria-label="showPassword ? 'Hide password' : 'Show password'"
          @click.stop="showPassword = !showPassword"
        >
          <EyeOff v-if="showPassword" class="h-4 w-4" />
          <Eye v-else class="h-4 w-4" />
        </button>
      </span>
    </div>

    <p
      v-if="isPassword && capsLockActive"
      class="mt-1.5 flex items-center gap-1 text-[11px] font-medium text-amber-600 dark:text-amber-400"
      role="status"
    >
      <ArrowBigUp class="h-3.5 w-3.5" />
      Caps Lock is on
    </p>
  </div>
</template>

<script setup>
import { ref, computed, inject, useAttrs, useSlots } from 'vue'
import { Eye, EyeOff, X, ArrowBigUp } from 'lucide-vue-next'
import { cn } from '../../utils/cn'
import { controlBase, controlInvalid, controlDisabled } from './controlStyles'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: '',
  },
  type: {
    type: String,
    default: 'text',
  },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg'].includes(v),
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
  error: {
    type: Boolean,
    default: false,
  },
  prefix: {
    type: String,
    default: '',
  },
  suffix: {
    type: String,
    default: '',
  },
  clearable: {
    type: Boolean,
    default: false,
  },
  autocomplete: {
    type: String,
    default: undefined,
  },
  ariaDescribedby: {
    type: String,
    default: undefined,
  },
})

const emit = defineEmits(['update:modelValue', 'input', 'change', 'blur', 'focus'])

const attrs = useAttrs()
const slots = useSlots()
const fieldCtx = inject('formField', null)
const inputId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)

// Everything except `class` (handled above) goes onto the native input, so
// attributes such as step, min, max, inputmode and maxlength actually work.
const inputAttrs = computed(() => {
  const { class: _c, ...rest } = attrs
  return rest
})

const inputRef = ref(null)
const showPassword = ref(false)
const capsLockActive = ref(false)

const isPassword = computed(() => props.type === 'password')
const isInvalid = computed(() => props.invalid || props.error || !!fieldCtx?.invalid?.value)

const computedType = computed(() => {
  if (isPassword.value) return showPassword.value ? 'text' : 'password'
  return props.type
})

const wrapperSize = computed(() => ({
  sm: 'h-8 rounded-md',
  md: 'h-9 rounded-lg',
  lg: 'h-11 rounded-lg',
}[props.size]))

const textSize = computed(() => (props.size === 'sm' ? 'text-xs' : 'text-sm'))
const padX = computed(() => (props.size === 'sm' ? 'px-2.5' : props.size === 'lg' ? 'px-3.5' : 'px-3'))

const showClear = computed(
  () => props.clearable && props.modelValue !== '' && props.modelValue !== null && props.modelValue !== undefined && !props.disabled && !props.readonly
)
const hasTrailing = computed(() => Boolean(showClear.value || props.suffix || slots.suffix || isPassword.value))

function handleInput(e) {
  let val = e.target.value
  if (props.type === 'number') {
    val = val === '' ? null : Number(val)
  }
  emit('update:modelValue', val)
  emit('input', e)
}

function clear() {
  emit('update:modelValue', props.type === 'number' ? null : '')
  inputRef.value?.focus()
}

function handleKeyState(e) {
  if (isPassword.value && e.getModifierState) {
    capsLockActive.value = e.getModifierState('CapsLock')
  }
}

function focus() {
  inputRef.value?.focus()
}

defineExpose({ focus, inputRef })
</script>
