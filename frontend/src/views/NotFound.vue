<template>
  <div class="min-h-[70vh] flex items-center justify-center p-6 animate-in fade-in duration-300">
    <div class="max-w-md w-full text-center space-y-6">
      <!-- Icon with glowing aura -->
      <div class="relative inline-flex items-center justify-center">
        <div class="w-24 h-24 rounded-3xl bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center justify-center ring-1 ring-brand-500/20 shadow-xl shadow-brand-500/10">
          <Compass class="w-12 h-12 stroke-[1.5] animate-spin-slow" />
        </div>
      </div>

      <!-- Text Details -->
      <div class="space-y-2">
        <p class="font-mono text-xs font-semibold text-brand-600 dark:text-brand-400 uppercase tracking-widest">
          Error 404
        </p>
        <h1 class="text-3xl font-bold tracking-tight text-primary">
          Route Not Found
        </h1>
        <p class="text-sm text-secondary leading-relaxed max-w-sm mx-auto">
          The dispatch destination, order record, or system page you requested does not exist or has been relocated.
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
        <Button variant="outline" class="w-full sm:w-auto" @click="goBack">
          <ArrowLeft class="w-4 h-4 mr-1.5" />
          <span>Go back</span>
        </Button>
        <Button class="w-full sm:w-auto" as-child>
          <router-link to="/dashboard">
            <Home class="w-4 h-4 mr-1.5" />
            <span>Dashboard</span>
          </router-link>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Compass, ArrowLeft, Home } from 'lucide-vue-next'
import Button from '../components/ui/Button.vue'

const router = useRouter()

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/dashboard')
  }
}
</script>

<style scoped>
@keyframes spinSlow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin-slow {
  animation: spinSlow 30s linear infinite;
}

@media (prefers-reduced-motion: reduce) {
  .animate-spin-slow {
    animation: none;
  }
}
</style>
