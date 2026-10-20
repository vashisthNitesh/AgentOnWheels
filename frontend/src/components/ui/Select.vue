<template>
  <SelectRoot
    :model-value="internalValue"
    :disabled="disabled"
    @update:model-value="handleUpdate"
    @update:open="isOpen = $event"
  >
    <SelectTrigger
      :id="triggerId"
      v-bind="restAttrs"
      :aria-invalid="isInvalid || undefined"
      :aria-describedby="ariaDescribedby || fieldCtx?.describedBy?.value"
      :class="cn(
        controlBase,
        'flex items-center justify-between gap-2 text-left select-none cursor-pointer',
        controlSizes[size],
        isInvalid ? controlInvalid : (isOpen ? controlOpen : controlIdle),
        disabled && controlDisabled,
        $attrs.class
      )"
    >
      <span class="block min-w-0 flex-1 truncate">
        <span v-if="selectedOption" class="text-primary">{{ selectedOption.label }}</span>
        <span v-else class="text-muted">{{ placeholder }}</span>
      </span>

      <span class="flex shrink-0 items-center gap-1">
        <span
          v-if="clearable && hasValue && !disabled"
          role="button"
          tabindex="-1"
          class="rounded p-0.5 text-muted transition hover:bg-subtle hover:text-primary"
          aria-label="Clear selection"
          @pointerdown.stop.prevent="handleClear"
        >
          <X class="h-3.5 w-3.5" />
        </span>
        <ChevronDown :class="cn('h-4 w-4 text-muted transition-transform duration-150', isOpen && 'rotate-180')" />
      </span>
    </SelectTrigger>

    <SelectPortal>
      <SelectContent
        position="popper"
        :side-offset="6"
        :collision-padding="12"
        :class="cn(
          floatingPanel,
          'z-dropdown min-w-[var(--reka-select-trigger-width)] max-h-[min(340px,var(--reka-select-content-available-height))] overflow-hidden'
        )"
      >
        <SelectScrollUpButton class="flex items-center justify-center py-1 text-muted">
          <ChevronUp class="h-4 w-4" />
        </SelectScrollUpButton>

        <SelectViewport class="p-1">
          <template v-for="(groupOpts, groupName) in groupedOptions" :key="groupName">
            <SelectGroup>
              <SelectLabel
                v-if="groupName !== '__default__'"
                class="px-2.5 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wider text-muted"
              >
                {{ groupName }}
              </SelectLabel>

              <SelectItem
                v-for="opt in groupOpts"
                :key="opt.key"
                :value="opt.key"
                :disabled="opt.disabled"
                :class="cn(
                  optionRow,
                  'pr-8 text-primary data-[highlighted]:bg-subtle data-[state=checked]:font-medium data-[state=checked]:text-primary-700 dark:data-[state=checked]:text-primary-300',
                  'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
                  size === 'sm' && 'py-1.5 text-xs'
                )"
              >
                <div class="flex min-w-0 flex-1 flex-col">
                  <SelectItemText class="truncate">{{ opt.label }}</SelectItemText>
                  <span v-if="opt.description" class="truncate text-[11px] text-muted">
                    {{ opt.description }}
                  </span>
                </div>

                <SelectItemIndicator class="absolute right-2.5 flex items-center text-primary-600 dark:text-primary-400">
                  <Check class="h-4 w-4" />
                </SelectItemIndicator>
              </SelectItem>
            </SelectGroup>
          </template>

          <div v-if="!normalizedOptions.length" class="px-3 py-6 text-center text-xs text-muted">
            No options available
          </div>
        </SelectViewport>

        <SelectScrollDownButton class="flex items-center justify-center py-1 text-muted">
          <ChevronDown class="h-4 w-4" />
        </SelectScrollDownButton>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>

<script setup>
import { ref, computed, inject, useAttrs } from 'vue'
import {
  SelectRoot,
  SelectTrigger,
  SelectPortal,
  SelectContent,
  SelectViewport,
  SelectItem,
  SelectItemText,
  SelectItemIndicator,
  SelectGroup,
  SelectLabel,
  SelectScrollUpButton,
  SelectScrollDownButton,
} from 'reka-ui'
import { ChevronDown, ChevronUp, Check, X } from 'lucide-vue-next'
import { cn } from '../../utils/cn'
import {
  controlBase, controlSizes, controlIdle, controlOpen, controlInvalid, controlDisabled,
  floatingPanel, optionRow,
} from './controlStyles'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean, null],
    default: null,
  },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Select…' },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg'].includes(v),
  },
  id: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  invalid: { type: Boolean, default: false },
  error: { type: Boolean, default: false },
  clearable: { type: Boolean, default: false },
  ariaDescribedby: { type: String, default: undefined },
})

const emit = defineEmits(['update:modelValue', 'change', 'clear', 'blur'])

const attrs = useAttrs()
const restAttrs = computed(() => {
  const { class: _c, ...rest } = attrs
  return rest
})

const fieldCtx = inject('formField', null)
const triggerId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)
const isInvalid = computed(() => props.invalid || props.error || !!fieldCtx?.invalid?.value)
const isOpen = ref(false)

// reka-ui forbids empty-string item values, and "All …" options commonly use
// '' / null / undefined. Every option gets a stable string key instead.
const EMPTY_KEY = '__aow_empty__'
const toKey = (v) => (v === undefined || v === null || v === '' ? EMPTY_KEY : String(v))

const normalizedOptions = computed(() =>
  props.options.map((opt) => {
    if (typeof opt === 'object' && opt !== null) {
      const value = 'value' in opt ? opt.value : opt.id
      return {
        value,
        key: toKey(value),
        label: opt.label ?? opt.name ?? String(value ?? ''),
        description: opt.description,
        disabled: opt.disabled,
        group: opt.group || '__default__',
      }
    }
    return { value: opt, key: toKey(opt), label: String(opt), group: '__default__' }
  })
)

const internalValue = computed(() => {
  const key = toKey(props.modelValue)
  // Only pass a key reka knows about; otherwise show the placeholder.
  return normalizedOptions.value.some((o) => o.key === key) ? key : undefined
})

const selectedOption = computed(() => {
  const key = toKey(props.modelValue)
  return normalizedOptions.value.find((o) => o.key === key) || null
})

const hasValue = computed(() => props.modelValue !== null && props.modelValue !== undefined && props.modelValue !== '')

const groupedOptions = computed(() => {
  const groups = {}
  for (const opt of normalizedOptions.value) {
    ;(groups[opt.group] ||= []).push(opt)
  }
  return groups
})

function handleUpdate(key) {
  const match = normalizedOptions.value.find((o) => o.key === key)
  const finalVal = match ? match.value : null
  emit('update:modelValue', finalVal)
  emit('change', finalVal)
}

function handleClear() {
  emit('update:modelValue', null)
  emit('change', null)
  emit('clear')
}
</script>
