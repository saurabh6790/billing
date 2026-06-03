<template>
  <div class="rounded-lg bg-surface-white p-5 shadow-sm">
    <p class="text-sm text-ink-gray-6">{{ label }}</p>
    <p class="mt-1 text-2xl font-semibold text-ink-gray-9" :class="valueClass">{{ value }}</p>
    <p v-if="sub" class="mt-1 text-xs text-ink-gray-5">{{ sub }}</p>
  </div>
</template>
<script setup>
defineProps({ label: String, value: [String, Number], sub: String, valueClass: String });
</script>
