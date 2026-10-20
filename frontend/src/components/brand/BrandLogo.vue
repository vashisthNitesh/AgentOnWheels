<template>
  <div :class="['inline-flex items-center gap-2.5 select-none', $attrs.class]">
    <div
      :class="[
        'relative flex items-center justify-center shrink-0 rounded-xl transition-all duration-200 shadow-xs',
        sizeMap.box,
        variant === 'glass'
          ? 'bg-gradient-to-br from-primary-500/15 via-primary-600/20 to-indigo-600/30 border border-primary-500/30 text-primary-600 dark:text-primary-400 backdrop-blur-xs'
          : 'bg-primary-600 text-white dark:bg-primary-500'
      ]"
    >
      <svg
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        :class="sizeMap.icon"
      >
        <!-- Precision A-Arch -->
        <path
          d="M6.5 25.5L14.4 7C14.8 6.1 15.6 5.5 16.5 5.5C17.4 5.5 18.2 6.1 18.6 7L26.5 25.5"
          stroke="currentColor"
          stroke-width="2.8"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <!-- Connected Axle Crossbar -->
        <path
          d="M3.5 18H28.5"
          stroke="currentColor"
          stroke-width="2.8"
          stroke-linecap="round"
        />
        <!-- Wheel / Axle Hub Bearing -->
        <circle cx="16.5" cy="18" r="3.25" fill="currentColor" />
        <circle cx="16.5" cy="18" r="1.4" class="fill-white dark:fill-slate-950" />
      </svg>
    </div>

    <!-- Wordmark & Optional Badge -->
    <div v-if="withText" class="flex items-center gap-1.5 leading-none min-w-0">
      <span :class="['font-sans font-bold tracking-tight', invert ? 'text-white' : 'text-primary', sizeMap.text]">
        Axle
      </span>
      <span
        v-if="withBadge"
        :class="[
          'rounded px-1.5 py-0.5 text-[10px] font-semibold tracking-wider uppercase border',
          invert
            ? 'bg-white/10 text-white border-white/20'
            : 'bg-primary-500/10 text-primary-600 dark:text-primary-400 border-primary-500/20'
        ]"
      >
        TMS
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md', // 'sm' | 'md' | 'lg' | 'xl'
  },
  variant: {
    type: String,
    default: 'solid', // 'solid' | 'glass'
  },
  withText: {
    type: Boolean,
    default: true,
  },
  withBadge: {
    type: Boolean,
    default: false,
  },
  invert: {
    type: Boolean,
    default: false,
  },
})

const sizeMap = computed(() => {
  switch (props.size) {
    case 'sm':
      return { box: 'w-7 h-7 rounded-lg', icon: 'w-4 h-4', text: 'text-sm' }
    case 'lg':
      return { box: 'w-10 h-10 rounded-xl', icon: 'w-6 h-6', text: 'text-lg' }
    case 'xl':
      return { box: 'w-12 h-12 rounded-2xl', icon: 'w-7 h-7', text: 'text-2xl' }
    case 'md':
    default:
      return { box: 'w-8 h-8 rounded-lg', icon: 'w-4.5 h-4.5', text: 'text-base font-bold' }
  }
})
</script>
