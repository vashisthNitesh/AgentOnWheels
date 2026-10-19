import { toast } from 'vue-sonner'

/**
 * Enterprise Toast composable wrapping vue-sonner with design system defaults.
 */
export function useToast() {
  function success(message, options = {}) {
    return toast.success(message, {
      duration: options.action ? Infinity : (options.duration || 5000),
      ...options,
    })
  }

  function error(message, options = {}) {
    return toast.error(message, {
      duration: options.action ? Infinity : (options.duration || 8000),
      ...options,
    })
  }

  function warning(message, options = {}) {
    return toast.warning(message, {
      duration: options.action ? Infinity : (options.duration || 5000),
      ...options,
    })
  }

  function info(message, options = {}) {
    return toast.info(message, {
      duration: options.action ? Infinity : (options.duration || 5000),
      ...options,
    })
  }

  function loading(message, options = {}) {
    return toast.loading(message, options)
  }

  function promise(promiseInstance, { loading, success, error }) {
    return toast.promise(promiseInstance, { loading, success, error })
  }

  return {
    toast,
    success,
    error,
    warning,
    info,
    loading,
    promise,
    dismiss: (id) => toast.dismiss(id),
  }
}
