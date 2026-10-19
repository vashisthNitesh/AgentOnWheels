<template>
  <TabsRoot
    :model-value="modelValue"
    class="flex flex-col w-full"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <TabsList
      :class="cn(
        'flex items-center select-none',
        variant === 'underline' && 'border-b border-border-default gap-6',
        variant === 'pill' && 'gap-1.5 flex-wrap',
        variant === 'segmented' && 'bg-muted p-1 rounded-lg border border-border-default gap-1 inline-flex self-start',
        $attrs.class
      )"
    >
      <TabsTrigger
        v-for="t in tabs"
        :key="t.value"
        :value="t.value"
        :disabled="t.disabled"
        :class="cn(
          'inline-flex items-center gap-2 font-medium transition-all focus-ring disabled:opacity-50 disabled:pointer-events-none cursor-pointer',
          sizeClasses,
          variant === 'underline' && [
            'relative py-2.5 border-b-2 -mb-[2px]',
            modelValue === t.value
              ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400 font-semibold'
              : 'border-transparent text-secondary hover:text-primary hover:border-slate-300 dark:hover:border-slate-700'
          ],
          variant === 'pill' && [
            'rounded-full px-3 py-1',
            modelValue === t.value
              ? 'bg-primary-600 text-white shadow-xs dark:bg-primary-500'
              : 'bg-subtle text-secondary hover:text-primary hover:bg-muted'
          ],
          variant === 'segmented' && [
            'rounded-md px-3 py-1',
            modelValue === t.value
              ? 'bg-surface text-primary font-semibold shadow-xs'
              : 'text-secondary hover:text-primary'
          ]
        )"
      >
        <component :is="t.icon" v-if="t.icon" class="w-4 h-4 shrink-0" />
        <span>{{ t.label }}</span>
        <span
          v-if="t.count !== undefined && t.count !== null"
          :class="cn(
            'text-[11px] font-semibold rounded-full px-1.5 py-0.2 shrink-0 tabular-nums',
            variant === 'pill' && modelValue === t.value
              ? 'bg-white/20 text-white'
              : 'bg-muted text-secondary'
          )"
        >
          {{ t.count }}
        </span>
      </TabsTrigger>
    </TabsList>

    <div v-if="$slots.default" class="mt-4">
      <slot />
    </div>
  </TabsRoot>
</template>

<script setup>
import { computed } from 'vue'
import { TabsRoot, TabsList, TabsTrigger } from 'reka-ui'
import { cn } from '../../utils/cn'

const props = defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  tabs: {
    type: Array,
    default: () => [],
  },
  variant: {
    type: String,
    default: 'underline',
    validator: v => ['underline', 'pill', 'segmented'].includes(v),
  },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md'].includes(v),
  },
})

defineEmits(['update:modelValue'])

const sizeClasses = computed(() => {
  return {
    sm: 'text-xs',
    md: 'text-sm',
  }[props.size]
})
</script>
