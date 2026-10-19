<template>
  <SelectRoot
    :model-value="modelValue !== null && modelValue !== undefined ? String(modelValue) : undefined"
    :disabled="disabled"
    @update:model-value="handleUpdate"
  >
    <div class="relative w-full">
      <SelectTrigger
        :id="triggerId"
        :aria-invalid="invalid || fieldCtx?.invalid?.value"
        :aria-describedby="ariaDescribedby || fieldCtx?.describedBy?.value"
        :class="cn(
          'w-full flex items-center justify-between bg-surface text-primary border rounded-md transition text-left focus-ring select-none',
          sizeClasses,
          (invalid || fieldCtx?.invalid?.value)
            ? 'border-danger-500 focus:border-danger-500 ring-2 ring-danger-500/20'
            : 'border-border-strong hover:border-slate-400 dark:hover:border-slate-500 focus:border-primary-500',
          disabled && 'opacity-60 cursor-not-allowed bg-muted pointer-events-none',
          $attrs.class
        )"
      >
        <span class="truncate block flex-1">
          <span v-if="selectedOption">{{ selectedOption.label }}</span>
          <span v-else class="text-muted font-normal">{{ placeholder }}</span>
        </span>

        <div class="flex items-center gap-1 ml-2 shrink-0">
          <button
            v-if="clearable && modelValue !== null && modelValue !== undefined && modelValue !== '' && !disabled"
            type="button"
            tabindex="-1"
            class="text-secondary hover:text-primary p-0.5 rounded transition"
            aria-label="Clear selection"
            @click.stop="handleClear"
          >
            <X class="w-3.5 h-3.5" />
          </button>
          <SelectIcon as-child>
            <ChevronDown class="w-4 h-4 text-secondary shrink-0" />
          </SelectIcon>
        </div>
      </SelectTrigger>

      <SelectPortal>
        <SelectContent
          position="popper"
          :side-offset="4"
          class="z-dropdown min-w-[180px] max-h-[320px] overflow-hidden rounded-lg border border-border-default bg-surface-raised bg-white dark:bg-slate-900 text-primary shadow-xl shadow-slate-950/15 dark:shadow-black/60 animate-in fade-in-80 zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2"
        >
          <SelectScrollUpButton class="flex items-center justify-center py-1 text-secondary cursor-default">
            <ChevronUp class="w-4 h-4" />
          </SelectScrollUpButton>

          <SelectViewport class="p-1">
            <template v-for="(groupOpts, groupName) in groupedOptions" :key="groupName">
              <SelectGroup>
                <SelectLabel v-if="groupName !== '__default__'" class="px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted">
                  {{ groupName }}
                </SelectLabel>

                <SelectItem
                  v-for="opt in groupOpts"
                  :key="opt.value"
                  :value="String(opt.value)"
                  :disabled="opt.disabled"
                  :class="cn(
                    'relative flex w-full cursor-pointer select-none items-center rounded-md px-2.5 py-1.5 text-xs outline-none transition-colors',
                    'hover:bg-subtle focus:bg-subtle focus:text-primary data-[highlighted]:bg-subtle',
                    'data-[disabled]:pointer-events-none data-[disabled]:opacity-50'
                  )"
                >
                  <div class="flex flex-col flex-1 pr-4">
                    <SelectItemText class="font-medium text-primary">
                      {{ opt.label }}
                    </SelectItemText>
                    <span v-if="opt.description" class="text-[11px] text-muted">
                      {{ opt.description }}
                    </span>
                  </div>

                  <SelectItemIndicator class="absolute right-2 flex items-center justify-center text-primary-600 dark:text-primary-400">
                    <Check class="w-3.5 h-3.5" />
                  </SelectItemIndicator>
                </SelectItem>
              </SelectGroup>
            </template>
          </SelectViewport>

          <SelectScrollDownButton class="flex items-center justify-center py-1 text-secondary cursor-default">
            <ChevronDown class="w-4 h-4" />
          </SelectScrollDownButton>
        </SelectContent>
      </SelectPortal>
    </div>
  </SelectRoot>
</template>

<script setup>
import { computed, inject } from 'vue'
import {
  SelectRoot,
  SelectTrigger,
  SelectIcon,
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

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null,
  },
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: 'Select…',
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
  disabled: {
    type: Boolean,
    default: false,
  },
  invalid: {
    type: Boolean,
    default: false,
  },
  clearable: {
    type: Boolean,
    default: false,
  },
  ariaDescribedby: {
    type: String,
    default: undefined,
  },
})

const emit = defineEmits(['update:modelValue', 'change', 'clear'])

const fieldCtx = inject('formField', null)
const triggerId = computed(() => props.id || fieldCtx?.fieldId?.value || undefined)

const sizeClasses = computed(() => {
  return {
    sm: 'h-8 text-xs px-2.5',
    md: 'h-9 text-sm px-3',
    lg: 'h-10 text-base px-3.5',
  }[props.size]
})

const normalizedOptions = computed(() => {
  return props.options.map(opt => {
    if (typeof opt === 'object' && opt !== null) {
      return {
        value: opt.value ?? opt.id,
        label: opt.label ?? opt.name ?? String(opt.value),
        description: opt.description,
        disabled: opt.disabled,
        group: opt.group || '__default__',
      }
    }
    return {
      value: opt,
      label: String(opt),
      group: '__default__',
    }
  })
})

const selectedOption = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '') return null
  return normalizedOptions.value.find(o => String(o.value) === String(props.modelValue))
})

const groupedOptions = computed(() => {
  const groups = {}
  for (const opt of normalizedOptions.value) {
    const g = opt.group || '__default__'
    if (!groups[g]) groups[g] = []
    groups[g].push(opt)
  }
  return groups
})

function handleUpdate(val) {
  if (val === undefined) {
    emit('update:modelValue', null)
    emit('change', null)
    return
  }
  const match = normalizedOptions.value.find(o => String(o.value) === String(val))
  const finalVal = match ? match.value : val
  emit('update:modelValue', finalVal)
  emit('change', finalVal)
}

function handleClear() {
  emit('update:modelValue', null)
  emit('change', null)
  emit('clear')
}
</script>
