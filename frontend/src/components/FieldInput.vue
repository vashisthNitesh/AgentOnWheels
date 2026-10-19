<template>
  <div :class="f.type === 'text' || f.type === 'm2m' ? 'sm:col-span-2' : ''">
    <label class="mb-1 block text-sm font-medium text-slate-700">{{ f.label }}<span v-if="f.required" class="text-rose-500"> *</span>
      <span v-if="f.name.endsWith('_t')" class="text-xs text-slate-400"> (tonnes)</span></label>
    <RefSelect v-if="f.type === 'fk' || f.type === 'm2m'" :resource="f.resource" :multiple="f.type === 'm2m'" :model-value="modelValue" :cls="{ 'input-err': error }" @update:model-value="emit" />
    <select v-else-if="f.type === 'choice'" :value="modelValue ?? ''" class="input" :class="{ 'input-err': error }" @change="emit($event.target.value)">
      <option value="" disabled>Select…</option><option v-for="c in f.choices" :key="c.value" :value="c.value">{{ c.label }}</option>
    </select>
    <label v-else-if="f.type === 'bool'" class="flex items-center gap-2 pt-2 text-sm"><input type="checkbox" :checked="modelValue" @change="emit($event.target.checked)" class="h-4 w-4" /> Yes</label>
    <textarea v-else-if="f.type === 'text'" :value="modelValue" rows="3" class="input" @input="emit($event.target.value)" />
    <input v-else-if="f.type === 'datetime'" type="datetime-local" :value="toLocal(modelValue)" class="input" :class="{ 'input-err': error }" @input="emit($event.target.value ? new Date($event.target.value).toISOString() : null)" />
    <input v-else :type="{ date: 'date', int: 'number', decimal: 'number', email: 'email' }[f.type] || 'text'" :step="f.type === 'decimal' ? '0.01' : undefined"
      :value="modelValue" class="input" :class="{ 'input-err': error }" @input="emit($event.target.value === '' ? null : $event.target.value)" />
    <p v-if="error" class="mt-1 text-xs text-rose-600">{{ error }}</p>
    <p v-else-if="f.help" class="mt-1 text-xs text-slate-400">{{ f.help }}</p>
  </div>
</template>
<script setup>
import RefSelect from './RefSelect.vue'
const p = defineProps({ f: Object, modelValue: null, error: String })
const e = defineEmits(['update:modelValue'])
const emit = v => e('update:modelValue', v)
const toLocal = v => { if (!v) return ''; const d = new Date(v); return new Date(d - d.getTimezoneOffset() * 6e4).toISOString().slice(0, 16) }
</script>
