<template>
  <div class="relative w-full flex items-center">
    <!-- Prefix / Unit slot -->
    <div
      v-if="$slots.prefix || prefix"
      class="absolute left-3 flex items-center pointer-events-none text-muted text-xs select-none"
    >
      <slot name="prefix">{{ prefix }}</slot>
    </div>

    <!-- Main Input -->
    <input
      :id="inputId"
      ref="inputRef"
      :name="name"
      :type="computedType"
      :value="modelValue ?? ''"
      :disabled="disabled"
      :readonly="readonly"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :aria-invalid="invalid || fieldCtx?.invalid?.value"
      :aria-describedby="ariaDescribedby || fieldCtx?.describedBy?.value"
      :class="cn(
        'w-full bg-surface text-primary border rounded-md transition placeholder:text-muted focus-ring',
        sizeClasses,
        (invalid || fieldCtx?.invalid?.value)
          ? 'border-danger-500 focus:border-danger-500 ring-2 ring-danger-500/20'
          : 'border-border-strong hover:border-slate-400 dark:hover:border-slate-500 focus:border-primary-500',
        disabled && 'opacity-60 cursor-not-allowed bg-muted pointer-events-none',
        readonly && 'bg-subtle cursor-default',
        (prefix || $slots.prefix) && 'pl-9',
        (suffix || $slots.suffix || isPassword || clearable) && 'pr-10',
        $attrs.class
      )"
      @input="handleInput"
      @keydown="handleKeyDown"
      @keyup="handleKeyUp"
      @focus="$emit('focus', $event)"
      @blur="$emit('blur', $event)"
    />

    <!-- Password visibility toggle -->
    <button
      v-if="isPassword"
      type="button"
      tabindex="-1"
      class="absolute right-3 text-secondary hover:text-primary transition p-0.5 rounded focus-ring"
      :aria-label="showPassword ? 'Hide password' : 'Show password'"
      @click="showPassword = !showPassword"
    >
      <EyeOff v-if="showPassword" class="w-4 h-4" />
      <Eye v-else class="w-4 h-4" />
    </button>

    <!-- Clearable button -->
    <button
      v-else-if="clearable && modelValue && !disabled && !readonly"
      type="button"
      tabindex="-1"
      class="absolute right-3 text-secondary hover:text-primary transition p-0.5 rounded focus-ring"
      aria-label="Clear input"
      @click="clear"
    >
      <X class="w-3.5 h-3.5" />
    </button>

    <!-- Suffix / Unit slot -->
    <div
      v-else-if="$slots.suffix || suffix"
      class="absolute right-3 flex items-center pointer-events-none text-muted text-xs select-none font-medium"
    >
      <slot name="suffix">{{ suffix }}</slot>
    </div>

    <!-- Caps lock alert for passwords -->
    <div
      v-if="isPassword && capsLockActive"
      class="absolute -bottom-5 right-0 text-[10px] text-amber-600 dark:text-amber-400 flex items-center gap-1 font-medium"
    >
      <span>⇪ Caps Lock is on</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { Eye, EyeOff, X } from 'lucide-vue-next'
import { cn } from '../../utils/cn'

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

const fieldCtx = inject('formField', null)
const inputId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)

const inputRef = ref(null)
const showPassword = ref(false)
const capsLockActive = ref(false)

const isPassword = computed(() => props.type === 'password')

const computedType = computed(() => {
  if (isPassword.value) {
    return showPassword.value ? 'text' : 'password'
  }
  return props.type
})

const sizeClasses = computed(() => {
  return {
    sm: 'h-8 text-xs px-2.5',
    md: 'h-9 text-sm px-3',
    lg: 'h-10 text-base px-3.5',
  }[props.size]
})

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

function handleKeyDown(e) {
  if (isPassword.value && e.getModifierState) {
    capsLockActive.value = e.getModifierState('CapsLock')
  }
}

function handleKeyUp(e) {
  if (isPassword.value && e.getModifierState) {
    capsLockActive.value = e.getModifierState('CapsLock')
  }
}

defineExpose({
  focus: () => inputRef.value?.focus(),
  inputRef,
})
</script>
