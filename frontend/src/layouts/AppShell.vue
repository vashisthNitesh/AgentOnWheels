<template>
  <!--
    The shell is locked to the viewport height. Only <main> scrolls, so the
    sidebar and topbar never move, and pages such as the resource list can
    fill the available height and manage their own internal scroll areas.
  -->
  <div class="flex h-dvh w-full overflow-hidden bg-app text-primary">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-tooltip focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded-md shadow-lg"
    >
      Skip to main content
    </a>

    <Sidebar
      :groups="groups"
      :mobile-open="mobileOpen"
      @close-mobile="mobileOpen = false"
    />

    <div class="flex min-w-0 flex-1 flex-col">
      <Topbar
        @open-mobile="mobileOpen = true"
        @open-search="commandPaletteRef?.open()"
      />

      <main
        id="main-content"
        ref="mainRef"
        tabindex="-1"
        class="relative min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden focus:outline-none"
      >
        <div class="flex min-h-full flex-col p-3 sm:p-4 lg:p-6">
          <slot />
        </div>
      </main>
    </div>

    <CommandPalette ref="commandPaletteRef" :groups="groups" />
    <ToastContainer />
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api, { auth } from '../api'
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'
import CommandPalette from './CommandPalette.vue'
import ToastContainer from '../components/feedback/ToastContainer.vue'
import ConfirmDialog from '../components/ui/ConfirmDialog.vue'

const groups = ref(null)
const mobileOpen = ref(false)
const commandPaletteRef = ref(null)
const mainRef = ref(null)
const route = useRoute()

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

// The window no longer scrolls, so reset the content pane on navigation.
watch(
  () => route.path,
  () => {
    mainRef.value?.scrollTo({ top: 0 })
    mobileOpen.value = false
  }
)

onMounted(loadMetadata)
watch(() => auth.user, loadMetadata)
</script>
