<template>
  <span v-if="f?.type === 'choice' && f.name.includes('status')" :class="['chip', STATUS_COLORS[row[name]] || 'bg-slate-100 text-slate-700']">{{ row[name + '_label'] }}</span>
  <span v-else-if="row[name + '_label'] !== undefined">{{ Array.isArray(row[name + '_label']) ? row[name + '_label'].join(', ') || '—' : row[name + '_label'] || '—' }}</span>
  <span v-else-if="typeof row[name] === 'boolean'">{{ row[name] ? '✔' : '—' }}</span>
  <span v-else-if="f?.type === 'datetime' || f?.type === 'date'">{{ fmtDate(row[name]) }}</span>
  <span v-else-if="f?.money">{{ fmtMoney(row[name], row.currency) }}</span>
  <span v-else-if="name.endsWith('_t')">{{ row[name] ?? '—' }} t</span>
  <span v-else>{{ row[name] ?? '—' }}</span>
</template>
<script setup>
import { fmtDate, fmtMoney, STATUS_COLORS } from '../format'
defineProps({ row: Object, name: String, f: Object })
</script>
