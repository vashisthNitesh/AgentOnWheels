<template>
  <div :class="cn('mb-6 space-y-3', $attrs.class)">
    <!-- Breadcrumbs row -->
    <Breadcrumbs v-if="breadcrumbs && breadcrumbs.length" :items="breadcrumbs" />

    <!-- Main Header Action Row -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="space-y-1 min-w-0">
        <div class="flex items-center gap-2.5">
          <component :is="icon" v-if="icon" class="w-6 h-6 text-primary-600 dark:text-primary-400 shrink-0" />
          <h1 class="text-2xl lg:text-3xl font-bold tracking-tight text-primary truncate">
            {{ title }}
          </h1>
          <slot name="title-badge" />
        </div>
        <p v-if="subtitle || $slots.subtitle" class="text-xs text-secondary">
          <slot name="subtitle">{{ subtitle }}</slot>
        </p>
      </div>

      <!-- Action Buttons -->
      <div v-if="$slots.actions" class="flex flex-wrap items-center gap-2.5 shrink-0">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { watchEffect } from 'vue'
import { cn } from '../utils/cn'
import Breadcrumbs from '../components/ui/Breadcrumbs.vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  icon: {
    type: [Object, Function],
    default: null,
  },
  breadcrumbs: {
    type: Array,
    default: () => [],
  },
})

watchEffect(() => {
  if (props.title) {
    document.title = `${props.title} · Axle`
  }
})
</script>
