<template>
  <div
    :class="cn(
      'relative inline-flex items-center justify-center rounded-full font-semibold select-none shrink-0 overflow-hidden ring-1 ring-border-default',
      sizeClasses,
      !src && bgClass,
      $attrs.class
    )"
  >
    <img
      v-if="src && !imgError"
      :src="src"
      :alt="alt || name"
      class="w-full h-full object-cover"
      @error="imgError = true"
    />
    <span v-else class="text-white uppercase font-medium">
      {{ initials }}
    </span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { cn } from '../../utils/cn'

const props = defineProps({
  src: {
    type: String,
    default: '',
  },
  name: {
    type: String,
    default: '',
  },
  alt: {
    type: String,
    default: '',
  },
  size: {
    type: [Number, String],
    default: 32,
    // Accepts pixel sizes (20/24/28/32/40) or names (xs/sm/md/lg).
  },
})

const imgError = ref(false)

const NAMED = { xs: 20, sm: 24, md: 32, lg: 40 }

const sizeClasses = computed(() => {
  const s = NAMED[props.size] ?? Number(props.size)
  return {
    20: 'w-5 h-5 text-[9px]',
    24: 'w-6 h-6 text-[10px]',
    28: 'w-7 h-7 text-[11px]',
    32: 'w-8 h-8 text-xs',
    40: 'w-10 h-10 text-sm',
  }[s] || 'w-8 h-8 text-xs'
})

const initials = computed(() => {
  if (!props.name) return '?'
  const parts = props.name.trim().split(/\s+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return parts[0].slice(0, 2).toUpperCase()
})

const bgColors = [
  'bg-indigo-600',
  'bg-teal-600',
  'bg-emerald-600',
  'bg-sky-600',
  'bg-violet-600',
  'bg-amber-600',
  'bg-rose-600',
  'bg-cyan-600',
]

const bgClass = computed(() => {
  if (!props.name) return 'bg-slate-600'
  let hash = 0
  for (let i = 0; i < props.name.length; i++) {
    hash = props.name.charCodeAt(i) + ((hash << 5) - hash)
  }
  const idx = Math.abs(hash) % bgColors.length
  return bgColors[idx]
})
</script>
