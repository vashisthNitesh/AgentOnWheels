import { ref } from 'vue'

const confirmState = ref({
  isOpen: false,
  title: 'Confirm action',
  message: 'Are you sure you want to proceed?',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  danger: false,
  requireMatch: '',
  resolve: null,
})

export function useConfirm() {
  function confirm(options = {}) {
    return new Promise((resolve) => {
      confirmState.value = {
        isOpen: true,
        title: options.title || 'Confirm action',
        message: options.message || 'Are you sure you want to proceed?',
        confirmText: options.confirmText || 'Confirm',
        cancelText: options.cancelText || 'Cancel',
        danger: !!options.danger,
        requireMatch: options.requireMatch || '',
        resolve,
      }
    })
  }

  function handleConfirm() {
    confirmState.value.isOpen = false
    if (confirmState.value.resolve) {
      confirmState.value.resolve(true)
      confirmState.value.resolve = null
    }
  }

  function handleCancel() {
    confirmState.value.isOpen = false
    if (confirmState.value.resolve) {
      confirmState.value.resolve(false)
      confirmState.value.resolve = null
    }
  }

  return {
    confirmState,
    confirm,
    handleConfirm,
    handleCancel,
  }
}
