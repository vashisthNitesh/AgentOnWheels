<template>
  <Modal
    :open="confirmState.isOpen"
    :title="confirmState.title"
    size="sm"
    @close="handleCancel"
  >
    <div class="space-y-4">
      <div class="flex items-start gap-3">
        <div
          :class="cn(
            'p-2.5 rounded-full shrink-0',
            confirmState.danger
              ? 'bg-danger-50 text-danger-600 dark:bg-danger-950/50 dark:text-danger-400'
              : 'bg-primary-50 text-primary-600 dark:bg-primary-950/50 dark:text-primary-400'
          )"
        >
          <AlertTriangle v-if="confirmState.danger" class="w-5 h-5" />
          <HelpCircle v-else class="w-5 h-5" />
        </div>
        <p class="text-sm text-secondary pt-1">
          {{ confirmState.message }}
        </p>
      </div>

      <!-- Confirmation Match requirement for destructive actions -->
      <div v-if="confirmState.requireMatch" class="space-y-1.5 pt-2">
        <label class="text-xs text-secondary font-medium">
          Type <code class="font-mono font-bold text-primary">{{ confirmState.requireMatch }}</code> to confirm:
        </label>
        <Input
          v-model="inputMatch"
          size="sm"
          :placeholder="confirmState.requireMatch"
          autocomplete="off"
        />
      </div>
    </div>

    <template #footer>
      <Button variant="ghost" size="sm" @click="handleCancel">
        {{ confirmState.cancelText }}
      </Button>
      <Button
        :variant="confirmState.danger ? 'danger' : 'primary'"
        size="sm"
        :disabled="isConfirmDisabled"
        @click="onConfirm"
      >
        {{ confirmState.confirmText }}
      </Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { AlertTriangle, HelpCircle } from 'lucide-vue-next'
import { useConfirm } from '../../composables/useConfirm'
import Modal from './Modal.vue'
import Button from './Button.vue'
import Input from './Input.vue'
import { cn } from '../../utils/cn'

const { confirmState, handleConfirm, handleCancel } = useConfirm()
const inputMatch = ref('')

watch(() => confirmState.value.isOpen, (open) => {
  if (open) inputMatch.value = ''
})

const isConfirmDisabled = computed(() => {
  if (!confirmState.value.requireMatch) return false
  return inputMatch.value.trim() !== confirmState.value.requireMatch.trim()
})

function onConfirm() {
  if (isConfirmDisabled.value) return
  handleConfirm()
}
</script>
