<template>
  <ResourceList :key="$route.params.key" />
</template>

<script setup>
import ResourceList from '../components/resource/ResourceList.vue'
</script>
