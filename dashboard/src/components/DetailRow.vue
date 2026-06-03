<template>
  <div class="flex items-start justify-between gap-4 border-b border-outline-gray-1 py-4 last:border-b-0">
    <div class="min-w-0">
      <p class="font-medium text-ink-gray-8">{{ label }}</p>
      <p class="mt-1 text-sm text-ink-gray-6"><slot name="desc" /></p>
    </div>
    <div class="shrink-0"><slot name="action" /></div>
  </div>
</template>
<script setup>
defineProps({ label: String });
</script>
