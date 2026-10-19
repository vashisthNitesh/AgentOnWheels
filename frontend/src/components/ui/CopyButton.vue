<template>
  <button
    type="button"
    :class="cn(
      'inline-flex items-center justify-center rounded p-1 text-secondary hover:text-primary hover:bg-subtle transition active:scale-95 focus-ring',
      $attrs.class
    )"
    :title="copied ? 'Copied!' : (title || 'Copy to clipboard')"
    :aria-label="title || 'Copy to clipboard'"
    @click.stop="copy"
  >
    <Check v-if="copied" class="w-3.5 h-3.5 text-success-600 dark:text-success-500 animate-in fade-in" />
    <Copy v-else class="w-3.5 h-3.5" />
  </button>
</template>

<script setup>
import { ref } from 'vue'
import { Copy, Check } from 'lucide-vue-next'
import { cn } from '../../utils/cn'

const props = defineProps({
  text: {
    type: [String, Number],
    required: true,
  },
  title: {
    type: String,
    default: '',
  },
})

const copied = ref(false)

async function copy() {
  if (!props.text) return
  try {
    await navigator.clipboard.writeText(String(props.text))
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 1500)
  } catch (err) {
    console.error('Failed to copy to clipboard', err)
  }
}
</script>
