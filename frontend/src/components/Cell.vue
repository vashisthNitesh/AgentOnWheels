<template>
  <CellDispatcher
    :row="row"
    :name="name"
    :field="f"
  />
</template>

<script setup>
import CellDispatcher from './data-table/cells/CellDispatcher.vue'
defineProps({ row: Object, name: String, f: Object })
</script>
