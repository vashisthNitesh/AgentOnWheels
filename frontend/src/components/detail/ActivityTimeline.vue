<template>
  <Card class="p-5 space-y-6">
    <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Audit Trail & Activity
      </h3>
      <span class="text-xs text-slate-400">{{ items.length }} logged events</span>
    </div>

    <!-- Timeline Days -->
    <div v-if="items.length > 0" class="space-y-6 relative before:absolute before:inset-0 before:left-4 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
      <div
        v-for="item in items"
        :key="item.id || item.timestamp"
        class="relative flex items-start gap-4"
      >
        <!-- Icon Marker -->
        <div
          :class="[
            'h-8 w-8 rounded-full flex items-center justify-center text-white shrink-0 shadow-xs z-10',
            item.tone === 'success'
              ? 'bg-emerald-500'
              : item.tone === 'danger'
                ? 'bg-rose-500'
                : item.tone === 'warning'
                  ? 'bg-amber-500'
                  : 'bg-brand-600'
          ]"
        >
          <component :is="item.icon || Check" class="w-4 h-4" />
        </div>

        <!-- Content Box -->
        <div class="flex-1 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 text-xs space-y-1">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-slate-900 dark:text-slate-100">{{ item.title }}</span>
            <Tooltip :content="formatDateTime(item.timestamp)">
              <span class="text-[11px] text-slate-400 cursor-default">
                {{ formatRelative(item.timestamp) }}
              </span>
            </Tooltip>
          </div>

          <p v-if="item.description" class="text-slate-600 dark:text-slate-300">
            {{ item.description }}
          </p>

          <div v-if="item.actor" class="flex items-center gap-1.5 pt-1 text-[11px] text-slate-400">
            <Avatar :name="item.actor" size="xs" />
            <span>by {{ item.actor }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="py-8 text-center text-xs text-slate-400">
      No activity events recorded yet.
    </div>
  </Card>
</template>

<script setup>
import { Check } from 'lucide-vue-next'
import Card from '../ui/Card.vue'
import Avatar from '../ui/Avatar.vue'
import Tooltip from '../ui/Tooltip.vue'
import { formatRelative, formatDateTime } from '../../utils/format'

defineProps({
  items: {
    type: Array,
    default: () => [],
  },
})
</script>
