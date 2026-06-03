<template>
  <div class="space-y-8">
    <div class="grid grid-cols-2 gap-px overflow-hidden rounded-lg bg-outline-gray-2 sm:grid-cols-4">
      <div v-for="s in stats" :key="s.label" class="bg-surface-white p-5">
        <p class="text-sm text-ink-gray-6">{{ s.label }}</p>
        <p class="mt-1 text-2xl font-semibold" :class="s.cls || 'text-ink-gray-9'">{{ s.value }}</p>
        <p v-if="s.sub" class="mt-1 text-xs text-ink-gray-5">{{ s.sub }}</p>
      </div>
    </div>
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-lg border border-outline-gray-2 p-5"><p class="text-sm text-ink-gray-6">Total billed</p><p class="mt-1 text-xl font-semibold text-ink-gray-9">{{ money(sum.data?.total_billed) }}</p></div>
      <div class="rounded-lg border border-outline-gray-2 p-5"><p class="text-sm text-ink-gray-6">Collected</p><p class="mt-1 text-xl font-semibold text-ink-green-3">{{ money(sum.data?.total_collected) }}</p></div>
      <div class="rounded-lg border border-outline-gray-2 p-5"><p class="text-sm text-ink-gray-6">Outstanding</p><p class="mt-1 text-xl font-semibold text-ink-amber-3">{{ money(sum.data?.outstanding) }}</p></div>
    </div>
    <div class="flex gap-3">
      <Button label="View teams" @click="$router.push('/billing/admin/teams')" />
      <Button label="Analytics & drill-downs" @click="$router.push('/billing/admin/analytics')" />
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue';
import { Button, createResource } from 'frappe-ui';
import { money } from '../utils';
const m = createResource({ url: 'press_billing.admin.get_metrics', auto: true });
const sum = createResource({ url: 'press_billing.admin.get_summary', auto: true });
const stats = computed(() => [
  { label: 'MRR', value: money(m.data?.mrr) },
  { label: 'Teams', value: m.data?.team_count ?? 0, sub: `${m.data?.paying_on_time ?? 0} on time` },
  { label: 'Delinquent', value: m.data?.delinquent ?? 0, sub: `${m.data?.suspended ?? 0} suspended`, cls: 'text-ink-amber-3' },
  { label: 'Payment failures', value: m.data?.payment_failures ?? 0, cls: 'text-ink-red-3' },
]);
</script>
