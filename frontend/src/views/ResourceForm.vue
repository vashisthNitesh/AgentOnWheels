<template>
  <!-- Loading -->
  <div v-if="loading || !meta" class="mx-auto w-full max-w-5xl space-y-5">
    <div class="h-4 w-32 animate-pulse rounded bg-muted" />
    <div class="h-8 w-72 animate-pulse rounded bg-muted" />
    <div class="h-[420px] w-full animate-pulse rounded-xl bg-muted/60" />
  </div>

  <div v-else class="-mb-3 flex flex-1 flex-col sm:-mb-4 lg:-mb-6">
    <div class="mx-auto w-full max-w-6xl flex-1 space-y-5 pb-8">
      <!-- Breadcrumb + autosave -->
      <div class="flex items-center justify-between gap-3">
        <router-link
          :to="backUrl"
          class="inline-flex items-center gap-1.5 rounded-md text-[13px] font-medium text-muted transition-colors hover:text-primary focus-ring"
        >
          <ArrowLeft class="h-4 w-4" />
          {{ recordId ? 'Back to record' : `Back to ${meta.title}` }}
        </router-link>

        <Transition
          enter-active-class="transition duration-200"
          enter-from-class="opacity-0"
          leave-active-class="transition duration-200"
          leave-to-class="opacity-0"
        >
          <span v-if="draftSavedAt" class="inline-flex items-center gap-1.5 text-xs text-muted">
            <CloudCheck class="h-3.5 w-3.5 text-success-500" />
            Draft saved {{ formatTime(draftSavedAt) }}
          </span>
        </Transition>
      </div>

      <!-- Title -->
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-border-default bg-surface text-primary-600 shadow-xs dark:text-primary-400">
          <component :is="moduleIcon" class="h-5 w-5" />
        </div>
        <div class="min-w-0">
          <h1 class="flex flex-wrap items-center gap-2 text-xl font-semibold tracking-tight text-primary">
            {{ recordId ? 'Edit' : 'New' }} {{ singularTitle.toLowerCase() }}
            <span v-if="recordId" class="rounded-md bg-muted px-2 py-0.5 font-mono text-sm font-medium text-secondary">
              {{ formData.number || formData.code || `#${recordId}` }}
            </span>
          </h1>
          <p class="mt-0.5 text-[13px] text-muted">
            {{ recordId ? 'Update the details below and save your changes.' : `Fill in the details to create a new ${singularTitle.toLowerCase()}.` }}
            Fields marked <span class="text-danger-500">*</span> are required.
          </p>
        </div>
      </div>

      <!-- Draft restore -->
      <div
        v-if="hasDraftToRestore"
        class="flex flex-col justify-between gap-3 rounded-xl border border-amber-200 bg-amber-50 p-3.5 text-[13px] text-amber-900 sm:flex-row sm:items-center dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-200"
      >
        <div class="flex items-center gap-2.5">
          <History class="h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400" />
          <span>You have an unsaved draft from <b>{{ formatDateTime(draftTimestamp) }}</b>.</span>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <Button variant="ghost" size="sm" @click="discardDraft">Discard</Button>
          <Button variant="primary" size="sm" @click="restoreDraft">Restore draft</Button>
        </div>
      </div>

      <!-- Stepper -->
      <div v-if="steps.length > 1" class="rounded-xl border border-border-default bg-surface px-3 py-1.5 shadow-xs">
        <Stepper
          :steps="formattedSteps"
          :current-step="currentStep"
          :max-visited-step="maxVisitedStep"
          @step-click="goToStep"
        />
      </div>

      <div class="flex flex-col items-start gap-6 xl:flex-row">
        <form class="w-full min-w-0 flex-1 space-y-4" novalidate @submit.prevent="nextStep">
          <FormErrorSummary :errors="fieldErrors" :fields="meta.fields" />

          <section class="rounded-xl border border-border-default bg-surface shadow-xs">
            <header class="flex items-center justify-between gap-3 border-b border-border-default px-5 py-4 sm:px-6">
              <div>
                <h2 class="text-[15px] font-semibold text-primary">{{ currentStepObj?.title || 'Details' }}</h2>
                <p v-if="steps.length > 1" class="mt-0.5 text-xs text-muted">
                  Step {{ currentStep + 1 }} of {{ steps.length }}
                </p>
              </div>
              <span class="text-xs tabular-nums text-muted">
                {{ stepFilled }} / {{ currentStepObj?.fields.length || 0 }} filled
              </span>
            </header>

            <div class="grid grid-cols-1 gap-x-5 gap-y-5 p-5 sm:p-6 md:grid-cols-2">
              <FormFieldAdapter
                v-for="fieldName in currentStepObj?.fields"
                :key="fieldName"
                v-model="formData[fieldName]"
                :name="fieldName"
                :field="meta.fields[fieldName]"
                :error="fieldErrors[fieldName]"
                :currency="formData.currency || 'AED'"
                :class="isWide(fieldName) ? 'md:col-span-2' : ''"
                @blur="validateField(fieldName)"
                @fk-select="onFkSelect"
              />
              <p v-if="!currentStepObj?.fields.length" class="col-span-full py-8 text-center text-sm text-muted">
                Nothing to fill in on this step.
              </p>
            </div>
          </section>

          <!-- Lets Enter submit the form from any text input -->
          <button type="submit" class="hidden" tabindex="-1" aria-hidden="true" />
        </form>

        <FormSummarySidebar
          v-if="steps.length > 1"
          class="hidden xl:block"
          :steps="steps"
          :current-step="currentStep"
          :form-data="formData"
          :fields="meta.fields"
          :errors="fieldErrors"
          @go-to-step="goToStep"
        />
      </div>
    </div>

    <!-- Sticky action bar (inside the scroll area, never over the sidebar) -->
    <div class="sticky bottom-0 z-20 -mx-3 border-t border-border-default bg-surface/90 px-3 py-3 backdrop-blur-md sm:-mx-4 sm:px-4 lg:-mx-6 lg:px-6">
      <div class="mx-auto flex max-w-6xl items-center justify-between gap-3">
        <Button variant="ghost" size="md" @click="$router.push(backUrl)">Cancel</Button>

        <div class="flex items-center gap-2">
          <span v-if="isDirty" class="mr-2 hidden items-center gap-1.5 text-xs text-muted sm:inline-flex">
            <span class="h-1.5 w-1.5 rounded-full bg-amber-500" /> Unsaved changes
          </span>
          <Button v-if="currentStep > 0" variant="outline" size="md" @click="prevStep">
            <ChevronLeft class="h-4 w-4" />
            Back
          </Button>
          <Button variant="primary" size="md" :loading="saving" @click="nextStep">
            <template v-if="isLastStep">
              <Check class="h-4 w-4" />
              {{ recordId ? 'Save changes' : `Create ${singularTitle.toLowerCase()}` }}
            </template>
            <template v-else>
              Continue
              <ChevronRight class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, CloudCheck, History, ChevronLeft, ChevronRight, Check } from 'lucide-vue-next'
import { getModuleIcon } from '../layouts/moduleIcons'
import { useResourceForm } from '../composables/useResourceForm'
import { formatDateTime } from '../utils/format'

import Button from '../components/ui/Button.vue'
import Stepper from '../components/ui/Stepper.vue'
import FormFieldAdapter from '../components/form/FormFieldAdapter.vue'
import FormErrorSummary from '../components/form/FormErrorSummary.vue'
import FormSummarySidebar from '../components/form/FormSummarySidebar.vue'

const route = useRoute()
const resourceKey = computed(() => route.params.key)
const recordId = computed(() => route.params.id)

const meta = ref(null)

const {
  formData,
  fieldErrors,
  currentStep,
  steps,
  saving,
  loading,
  isDirty,
  hasDraftToRestore,
  draftTimestamp,
  draftSavedAt,
  validateField,
  goToStep,
  nextStep,
  prevStep,
  restoreDraft,
  discardDraft,
  onFkSelect,
} = useResourceForm(resourceKey, recordId, meta)

const maxVisitedStep = ref(0)
watch(currentStep, (step) => {
  if (step > maxVisitedStep.value) {
    maxVisitedStep.value = step
  }
})

const backUrl = computed(() => {
  if (recordId.value) {
    return resourceKey.value === 'orders' ? `/orders/${recordId.value}` : `/r/${resourceKey.value}/${recordId.value}`
  }
  return `/r/${resourceKey.value}`
})

const singularTitle = computed(() => {
  const t = meta.value?.title || 'Record'
  if (t.endsWith('ies')) return `${t.slice(0, -3)}y`
  return t.endsWith('s') ? t.slice(0, -1) : t
})

const moduleIcon = computed(() => getModuleIcon(resourceKey.value))

function isWide(fieldName) {
  const f = meta.value?.fields?.[fieldName]
  return f?.type === 'text' || f?.type === 'm2m' || ['notes', 'remarks', 'description'].includes(fieldName) || fieldName.includes('address')
}

const stepFilled = computed(() => {
  const fields = currentStepObj.value?.fields || []
  return fields.filter((f) => {
    const v = formData[f]
    return v !== undefined && v !== null && v !== '' && !(Array.isArray(v) && !v.length)
  }).length
})

const currentStepObj = computed(() => steps.value[currentStep.value])
const isLastStep = computed(() => currentStep.value >= steps.value.length - 1)

const formattedSteps = computed(() => {
  return steps.value.map((s) => ({
    title: s.title,
    hasError: s.fields.some((f) => !!fieldErrors.value[f]),
  }))
})

function formatTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>
