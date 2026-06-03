<template>
  <div class="rounded-lg bg-surface-white shadow-sm">
    <div v-if="title || $slots.actions" class="flex items-center justify-between border-b border-outline-gray-1 px-5 py-3">
      <h2 class="text-base font-semibold text-ink-gray-8">{{ title }}</h2>
      <div><slot name="actions" /></div>
    </div>
    <div :class="bodyClass || 'p-5'"><slot /></div>
  </div>
</template>
<script setup>
defineProps({ title: String, bodyClass: String });
</script>
