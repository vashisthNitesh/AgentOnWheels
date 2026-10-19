<template>
  <div class="flex min-h-screen bg-app text-primary">
    <!-- Skip to main content accessibility link -->
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-tooltip focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded-md shadow-lg"
    >
      Skip to main content
    </a>

    <!-- Sidebar Navigation -->
    <Sidebar
      :groups="groups"
      :mobile-open="mobileOpen"
      @close-mobile="mobileOpen = false"
    />

    <!-- Main Viewport -->
    <div class="flex min-w-0 flex-1 flex-col">
      <!-- Sticky Topbar -->
      <Topbar
        @open-mobile="mobileOpen = true"
        @open-search="commandPaletteRef?.open()"
      />

      <!-- Page Content Slot -->
      <main id="main-content" class="min-w-0 flex-1 p-4 lg:p-6 focus:outline-none">
        <slot />
      </main>
    </div>

    <!-- Global Floating Command Palette -->
    <CommandPalette ref="commandPaletteRef" :groups="groups" />

    <!-- Global Toasters & Confirmation Modals -->
    <ToastContainer />
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api, { auth } from '../api'
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'
import CommandPalette from './CommandPalette.vue'
import ToastContainer from '../components/feedback/ToastContainer.vue'
import ConfirmDialog from '../components/ui/ConfirmDialog.vue'

const groups = ref(null)
const mobileOpen = ref(false)
const commandPaletteRef = ref(null)

async function loadMetadata() {
  if (auth.user && !groups.value) {
    try {
      const res = await api.get('meta/')
      groups.value = res.data.groups
    } catch (err) {
      console.error('Failed to load navigation metadata', err)
    }
  }
}

onMounted(() => {
  loadMetadata()
})

watch(() => auth.user, loadMetadata)
</script>
