<template>
  <nav aria-label="Breadcrumb" :class="cn('flex items-center text-xs text-secondary select-none', $attrs.class)">
    <ol class="flex items-center gap-1.5 flex-wrap">
      <li v-for="(item, idx) in items" :key="idx" class="flex items-center gap-1.5">
        <ChevronRight v-if="idx > 0" class="w-3.5 h-3.5 text-muted shrink-0" />

        <router-link
          v-if="item.to && idx < items.length - 1"
          :to="item.to"
          class="hover:text-primary transition-colors flex items-center gap-1 font-medium hover:underline"
        >
          <component :is="item.icon" v-if="item.icon" class="w-3.5 h-3.5 shrink-0" />
          <span class="truncate max-w-[160px]">{{ item.label }}</span>
        </router-link>

        <span
          v-else
          :class="[
            'truncate max-w-[200px]',
            idx === items.length - 1 ? 'font-semibold text-primary' : 'text-secondary'
          ]"
          :aria-current="idx === items.length - 1 ? 'page' : undefined"
        >
          {{ item.label }}
        </span>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { ChevronRight } from 'lucide-vue-next'
import { cn } from '../../utils/cn'

defineProps({
  items: {
    type: Array,
    required: true,
  },
})
</script>
