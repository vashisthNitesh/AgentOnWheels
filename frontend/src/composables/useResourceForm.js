import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { z } from 'zod'
import api, { errText } from '../api'
import { useToast } from './useToast'
import { useConfirm } from './useConfirm'

/**
 * useResourceForm
 * Manages full lifecycle of registry-driven forms and wizards:
 * - Dynamic Zod validation schemas
 * - Multi-step navigation with step validation
 * - Autosave drafts to localStorage with restore/discard prompt
 * - Unsaved changes navigation guard
 * - Server error mapping
 * - Dependent field auto-fill
 */
export function useResourceForm(resourceKeyRef, recordIdRef, metaRef) {
  const router = useRouter()
  const toast = useToast()
  const confirm = useConfirm()

  const key = computed(() => resourceKeyRef.value || resourceKeyRef)
  const id = computed(() => recordIdRef.value || recordIdRef)

  // Form State
  const formData = reactive({})
  const initialData = ref({})
  const fieldErrors = ref({})
  const touchedFields = reactive({})
  const currentStep = ref(0)
  const saving = ref(false)
  const loading = ref(true)

  // Draft Autosave
  const draftKey = computed(() => `aow_draft_${key.value}_${id.value || 'new'}`)
  const draftSavedAt = ref(null)
  const hasDraftToRestore = ref(false)
  const draftTimestamp = ref(null)
  let autosaveTimer = null

  // Editable fields from meta
  const editableFields = computed(() => {
    if (!metaRef.value?.fields) return []
    return Object.values(metaRef.value.fields)
      .filter((f) => !f.readonly && f.type !== 'computed')
      .map((f) => f.name)
  })

  // Multi-step groups
  const steps = computed(() => {
    if (!metaRef.value) return [{ title: 'Details', fields: [] }]
    const editable = editableFields.value

    if (metaRef.value.steps?.length) {
      const parsedSteps = metaRef.value.steps.map((s) => ({
        title: s.title,
        fields: s.fields.filter((f) => editable.includes(f)),
      }))
      const groupedFields = new Set(parsedSteps.flatMap((s) => s.fields))
      const leftover = editable.filter((f) => !groupedFields.has(f))
      if (leftover.length > 0) {
        parsedSteps.push({ title: 'Additional Details', fields: leftover })
      }
      return parsedSteps
    }

    return [{ title: 'General Information', fields: editable }]
  })

  // Dirty state tracking
  const isDirty = computed(() => {
    try {
      const a = JSON.stringify(formData)
      const b = JSON.stringify(initialData.value)
      return a !== b
    } catch {
      return false
    }
  })

  // Build Zod Schema dynamically for a given list of fields
  function buildZodSchema(fieldNames) {
    const shape = {}
    const metaFields = metaRef.value?.fields || {}

    for (const name of fieldNames) {
      const f = metaFields[name]
      if (!f) continue

      let validator = z.any()

      if (f.type === 'email' || name.includes('email')) {
        validator = f.required
          ? z.string().min(1, `${f.label} is required`).email('Invalid email address')
          : z.string().email('Invalid email address').optional().or(z.literal(''))
      } else if (f.type === 'int' || f.type === 'decimal' || f.type === 'float') {
        validator = f.required
          ? z.union([z.number(), z.string().min(1, `${f.label} is required`)])
          : z.any()
      } else if (f.type === 'bool') {
        validator = z.boolean().optional()
      } else if (f.type === 'm2m') {
        validator = f.required
          ? z.array(z.any()).min(1, `Please select at least one ${f.label.toLowerCase()}`)
          : z.array(z.any()).optional()
      } else if (f.required) {
        validator = z
          .any()
          .refine(
            (val) => val !== undefined && val !== null && val !== '',
            { message: `${f.label} is required` }
          )
      }

      shape[name] = validator
    }

    return z.object(shape)
  }

  // Validate a single field
  function validateField(fieldName) {
    touchedFields[fieldName] = true
    const schema = buildZodSchema([fieldName])
    const result = schema.safeParse({ [fieldName]: formData[fieldName] })

    if (!result.success) {
      const issue = result.error.issues[0]
      fieldErrors.value[fieldName] = issue.message
      return false
    } else {
      delete fieldErrors.value[fieldName]
      return true
    }
  }

  // Validate all fields in a specific step
  function validateStep(stepIndex) {
    const step = steps.value[stepIndex]
    if (!step) return true

    let isValid = true
    const schema = buildZodSchema(step.fields)
    const stepData = {}
    for (const f of step.fields) {
      touchedFields[f] = true
      stepData[f] = formData[f]
    }

    const result = schema.safeParse(stepData)
    if (!result.success) {
      isValid = false
      for (const issue of result.error.issues) {
        const fieldName = issue.path[0]
        fieldErrors.value[fieldName] = issue.message
      }
    } else {
      for (const f of step.fields) {
        delete fieldErrors.value[f]
      }
    }

    return isValid
  }

  // Autosave Draft
  function saveDraft() {
    if (!isDirty.value) return
    try {
      const draft = {
        savedAt: new Date().toISOString(),
        data: { ...formData },
        step: currentStep.value,
      }
      localStorage.setItem(draftKey.value, JSON.stringify(draft))
      draftSavedAt.value = new Date()
    } catch {}
  }

  function checkDraft() {
    try {
      const raw = localStorage.getItem(draftKey.value)
      if (raw) {
        const draft = JSON.parse(raw)
        hasDraftToRestore.value = true
        draftTimestamp.value = draft.savedAt
      }
    } catch {}
  }

  function restoreDraft() {
    try {
      const raw = localStorage.getItem(draftKey.value)
      if (raw) {
        const draft = JSON.parse(raw)
        Object.assign(formData, draft.data)
        if (draft.step !== undefined && draft.step < steps.value.length) {
          currentStep.value = draft.step
        }
        hasDraftToRestore.value = false
        toast.info('Draft restored')
      }
    } catch {}
  }

  function discardDraft() {
    try {
      localStorage.removeItem(draftKey.value)
      hasDraftToRestore.value = false
    } catch {}
  }

  // Watch formData changes for debounced autosave
  watch(
    formData,
    () => {
      clearTimeout(autosaveTimer)
      autosaveTimer = setTimeout(saveDraft, 1000)
    },
    { deep: true }
  )

  // Dependent field handling
  function onFkSelect({ name, value, option }) {
    if (!option?.raw) return
    const raw = option.raw

    // Dependent rule 1: Customer selection pre-fills payment terms & salesperson
    if (name === 'customer') {
      if (raw.payment_terms_days && formData.payment_terms_days === undefined) {
        formData.payment_terms_days = raw.payment_terms_days
      }
      if (raw.salesperson && formData.salesperson === undefined) {
        formData.salesperson = raw.salesperson
      }
      if (raw.billing_address && formData.pickup_address === undefined) {
        formData.pickup_address = raw.billing_address
      }
    }

    // Dependent rule 2: Country selection pre-fills currency
    if (name === 'country' && raw.currency) {
      formData.currency = raw.currency
      toast.info(`Currency auto-set to ${raw.currency}`)
    }
  }

  // Step Navigation
  function goToStep(index) {
    if (index === currentStep.value) return
    if (index > currentStep.value) {
      const stepValid = validateStep(currentStep.value)
      if (!stepValid) {
        toast.warning('Please correct the highlighted errors before continuing')
        return
      }
    }
    currentStep.value = index
  }

  function nextStep() {
    if (currentStep.value < steps.value.length - 1) {
      const valid = validateStep(currentStep.value)
      if (!valid) {
        toast.warning('Please fill in the required fields to proceed')
        return
      }
      currentStep.value++
    } else {
      submitForm()
    }
  }

  function prevStep() {
    if (currentStep.value > 0) {
      currentStep.value--
    }
  }

  // Submit Form
  async function submitForm() {
    // Validate all steps
    let allValid = true
    for (let i = 0; i < steps.value.length; i++) {
      if (!validateStep(i)) {
        allValid = false
        currentStep.value = i
        break
      }
    }

    if (!allValid) {
      toast.error('Please resolve all validation errors')
      return
    }

    saving.value = true
    fieldErrors.value = {}

    // Prepare payload
    const payload = {}
    for (const f of editableFields.value) {
      if (formData[f] !== undefined) {
        payload[f] = formData[f] === '' ? null : formData[f]
      }
    }

    try {
      let res
      if (id.value) {
        res = await api.patch(`${key.value}/${id.value}/`, payload)
        toast.success(`${metaRef.value?.title ? metaRef.value.title.slice(0, -1) : 'Record'} updated successfully`)
      } else {
        res = await api.post(`${key.value}/`, payload)
        toast.success(`${metaRef.value?.title ? metaRef.value.title.slice(0, -1) : 'Record'} created successfully`)
      }

      // Clear draft on successful save
      discardDraft()
      initialData.value = { ...formData }

      const recordId = res.data.id || id.value
      const targetUrl = key.value === 'orders' ? `/orders/${recordId}` : `/r/${key.value}/${recordId}`
      router.push(targetUrl)
    } catch (err) {
      const serverData = err.response?.data || {}
      if (typeof serverData === 'object' && !Array.isArray(serverData)) {
        for (const [k, v] of Object.entries(serverData)) {
          fieldErrors.value[k] = Array.isArray(v) ? v.join(' ') : String(v)
        }
      } else {
        fieldErrors.value.non_field_errors = errText(err)
      }

      // Jump to step with first error
      const firstErrorStep = steps.value.findIndex((s) => s.fields.some((f) => fieldErrors.value[f]))
      if (firstErrorStep !== -1) {
        currentStep.value = firstErrorStep
      }

      toast.error(errText(err))
    } finally {
      saving.value = false
    }
  }

  // Unsaved changes navigation guard
  onBeforeRouteLeave(async () => {
    if (isDirty.value && !saving.value) {
      const leave = await confirm.warning({
        title: 'Unsaved Changes',
        message: 'You have unsaved changes that will be lost. Are you sure you want to leave this page?',
        confirmText: 'Leave without saving',
        cancelText: 'Stay on page',
      })
      if (!leave) return false
    }
    return true
  })

  // Browser tab close guard
  function onBeforeUnload(e) {
    if (isDirty.value && !saving.value) {
      e.preventDefault()
      e.returnValue = ''
    }
  }

  // Load record if editing
  async function init() {
    loading.value = true
    try {
      metaRef.value = (await api.get(`meta/${key.value}/`)).data

      if (id.value) {
        const res = await api.get(`${key.value}/${id.value}/`)
        const record = res.data
        for (const f of editableFields.value) {
          formData[f] = record[f]
        }
      } else {
        // Defaults for create
        for (const f of editableFields.value) {
          if (metaRef.value.fields[f]?.type === 'bool') {
            formData[f] = false
          }
        }
        if (metaRef.value.fields.order_date && formData.order_date === undefined) {
          formData.order_date = new Date().toISOString().slice(0, 10)
        }
        if (metaRef.value.fields.currency && formData.currency === undefined) {
          formData.currency = 'AED'
        }
      }

      initialData.value = JSON.parse(JSON.stringify(formData))
      checkDraft()
    } catch (e) {
      toast.error(errText(e))
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    window.addEventListener('beforeunload', onBeforeUnload)
    init()
  })

  onUnmounted(() => {
    window.removeEventListener('beforeunload', onBeforeUnload)
    clearTimeout(autosaveTimer)
  })

  return {
    formData,
    fieldErrors,
    touchedFields,
    currentStep,
    steps,
    saving,
    loading,
    isDirty,
    hasDraftToRestore,
    draftTimestamp,
    draftSavedAt,
    validateField,
    validateStep,
    goToStep,
    nextStep,
    prevStep,
    submitForm,
    restoreDraft,
    discardDraft,
    onFkSelect,
  }
}
