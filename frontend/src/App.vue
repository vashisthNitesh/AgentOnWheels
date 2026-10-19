<template>
  <router-view v-if="$route.meta.public" />
  <AppShell v-else>
    <router-view :key="$route.fullPath.split('?')[0]" />
  </AppShell>
</template>

<script setup>
import AppShell from './layouts/AppShell.vue'
</script>
