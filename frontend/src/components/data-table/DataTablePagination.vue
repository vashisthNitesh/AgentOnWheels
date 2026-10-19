<template>
  <Pagination
    :page="page"
    :page-size="pageSize"
    :total="total"
    :page-sizes="[20, 50, 100]"
    @update:page="$emit('update:page', $event)"
    @update:page-size="$emit('update:pageSize', $event)"
    @change="$emit('change', $event)"
  />
</template>

<script setup>
import Pagination from '../ui/Pagination.vue'

defineProps({
  page: {
    type: Number,
    required: true,
  },
  pageSize: {
    type: Number,
    required: true,
  },
  total: {
    type: Number,
    required: true,
  },
})

defineEmits(['update:page', 'update:pageSize', 'change'])
</script>
