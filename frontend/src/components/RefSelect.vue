<template>
  <select v-if="!multiple" :value="modelValue ?? ''" class="input" :class="cls" @change="$emit('update:modelValue', $event.target.value === '' ? null : Number($event.target.value))">
    <option value="">{{ placeholder }}</option>
    <option v-for="o in opts" :key="o.id" :value="o.id">{{ o.display }}</option>
  </select>
  <select v-else multiple :value="modelValue || []" class="input h-32" :class="cls" @change="$emit('update:modelValue', [...$event.target.selectedOptions].map(o => Number(o.value)))">
    <option v-for="o in opts" :key="o.id" :value="o.id">{{ o.display }}</option>
  </select>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
const p = defineProps({ resource: String, modelValue: [Number, Array, String], multiple: Boolean, placeholder: { type: String, default: 'Select…' }, cls: [String, Object] })
defineEmits(['update:modelValue'])
const cache = (window.__refCache ||= {})
const opts = ref([])
onMounted(async () => {
  if (!p.resource) return
  cache[p.resource] ||= api.get(p.resource + '/', { params: { page_size: 500 } }).then(r => r.data.results)
  opts.value = await cache[p.resource]
})
</script>
