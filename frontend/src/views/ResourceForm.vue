<template>
  <!-- Loading Skeleton -->
  <div v-if="loading || !meta" class="max-w-5xl mx-auto p-4 sm:p-8 space-y-6">
    <div class="h-6 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
    <div class="h-10 w-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
    <div class="h-96 w-full bg-slate-100 dark:bg-slate-900 rounded-xl animate-pulse" />
  </div>

  <!-- Main Form / Wizard Container -->
  <div v-else class="max-w-6xl mx-auto p-4 sm:p-8 pb-32 space-y-6">
    <!-- Top Navigation / Breadcrumbs -->
    <div class="flex items-center justify-between">
      <router-link
        :to="backUrl"
        class="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors"
      >
        <ArrowLeft class="w-4 h-4" />
        <span>Back to {{ meta.title }}</span>
      </router-link>

      <!-- Autosave indicator -->
      <div v-if="draftSavedAt" class="flex items-center gap-1.5 text-xs text-slate-400">
        <CheckCircle2 class="w-3.5 h-3.5 text-emerald-500" />
        <span>Draft saved · {{ formatTime(draftSavedAt) }}</span>
      </div>
    </div>

    <!-- Page Title -->
    <div>
      <div class="flex items-center gap-2.5">
        <span class="text-2xl">{{ meta.icon || '📝' }}</span>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
          {{ recordId ? 'Edit' : 'New' }} {{ singularTitle }}
        </h1>
        <span v-if="recordId" class="font-mono text-sm px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-semibold">
          #{{ formData.number || formData.code || recordId }}
        </span>
      </div>
      <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
        {{ recordId ? 'Update fields and save changes' : `Complete the details below to create a new ${singularTitle.toLowerCase()}` }}.
      </p>
    </div>

    <!-- Draft Restoration Notice -->
    <div
      v-if="hasDraftToRestore"
      class="p-4 rounded-xl border border-amber-200 dark:border-amber-900/60 bg-amber-50/80 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-xs"
    >
      <div class="flex items-center gap-2">
        <AlertCircle class="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
        <span>
          A saved draft from <b>{{ formatDateTime(draftTimestamp) }}</b> was found. Would you like to restore it?
        </span>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          class="px-2.5 py-1 font-semibold rounded bg-amber-600 hover:bg-amber-700 text-white transition-colors"
          @click="restoreDraft"
        >
          Restore draft
        </button>
        <button
          type="button"
          class="px-2.5 py-1 font-medium rounded hover:bg-amber-100 dark:hover:bg-amber-900 text-amber-800 dark:text-amber-300 transition-colors"
          @click="discardDraft"
        >
          Discard
        </button>
      </div>
    </div>

    <!-- Stepper Wizard (if multi-step) -->
    <div v-if="steps.length > 1" class="py-2 border-y border-slate-200 dark:border-slate-800">
      <Stepper
        :steps="formattedSteps"
        :current-step="currentStep"
        :max-visited-step="maxVisitedStep"
        @step-click="goToStep"
      />
    </div>

    <!-- Form & Sticky Sidebar Layout -->
    <div class="flex flex-col xl:flex-row items-start gap-8">
      <!-- Main Form Body -->
      <form class="flex-1 w-full space-y-6" @submit.prevent="nextStep">
        <!-- Error Summary Banner -->
        <FormErrorSummary
          :errors="fieldErrors"
          :fields="meta.fields"
        />

        <!-- Active Step Card -->
        <Card class="p-6 space-y-6">
          <div class="border-b border-slate-100 dark:border-slate-800 pb-3">
            <h2 class="text-base font-semibold text-slate-900 dark:text-slate-100">
              {{ currentStepObj?.title || 'Details' }}
            </h2>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Fill in the required fields marked with an asterisk (*).
            </p>
          </div>

          <!-- Field Grid (2-column responsive layout) -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <template v-for="fieldName in currentStepObj?.fields" :key="fieldName">
              <FormFieldAdapter
                :name="fieldName"
                :field="meta.fields[fieldName]"
                v-model="formData[fieldName]"
                :error="fieldErrors[fieldName]"
                :currency="formData.currency || 'AED'"
                :class="[
                  meta.fields[fieldName]?.type === 'text' || fieldName === 'notes' || fieldName === 'remarks'
                    ? 'md:col-span-2'
                    : ''
                ]"
                @blur="validateField(fieldName)"
                @fk-select="onFkSelect"
              />
            </template>
          </div>
        </Card>
      </form>

      <!-- Sticky Summary Sidebar on Desktop (xl) -->
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

    <!-- Sticky Bottom Navigation Footer -->
    <div class="fixed bottom-0 left-0 right-0 z-30 p-3 sm:px-8 border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md shadow-lg">
      <div class="max-w-6xl mx-auto flex items-center justify-between gap-3">
        <!-- Cancel button -->
        <Button
          variant="ghost"
          size="sm"
          type="button"
          @click="$router.push(backUrl)"
        >
          Cancel
        </Button>

        <div class="flex items-center gap-2">
          <!-- Back button in wizard -->
          <Button
            v-if="currentStep > 0"
            variant="outline"
            size="sm"
            type="button"
            @click="prevStep"
          >
            <ChevronLeft class="w-4 h-4 mr-1" />
            Back
          </Button>

          <!-- Next or Submit button -->
          <Button
            variant="primary"
            size="sm"
            type="button"
            :loading="saving"
            @click="nextStep"
          >
            <span>{{ isLastStep ? (recordId ? 'Save changes' : 'Create ' + singularTitle) : 'Next' }}</span>
            <ChevronRight v-if="!isLastStep" class="w-4 h-4 ml-1" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
} from 'lucide-vue-next'
import { useResourceForm } from '../composables/useResourceForm'
import { formatDateTime } from '../utils/format'

import Card from '../components/ui/Card.vue'
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
  return t.endsWith('s') ? t.slice(0, -1) : t
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
