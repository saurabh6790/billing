<template>
  <div class="space-y-8">
    <div class="grid grid-cols-2 gap-px overflow-hidden rounded-lg bg-outline-gray-1 sm:grid-cols-4">
      <div v-for="s in stats" :key="s.label" class="bg-surface-white p-5">
        <p class="text-sm text-ink-gray-6">{{ s.label }}</p>
        <p class="mt-1 text-2xl font-semibold" :class="s.cls || 'text-ink-gray-9'">{{ s.value }}</p>
        <p v-if="s.sub" class="mt-1 text-xs text-ink-gray-5">{{ s.sub }}</p>
      </div>
    </div>
    <section>
      <h2 class="mb-2 text-base font-semibold text-ink-gray-9">Teams</h2>
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-outline-gray-2 text-left text-ink-gray-5">
            <th class="py-2.5 pr-4 font-normal">Team</th>
            <th class="py-2.5 pr-4 font-normal">Standing</th>
            <th class="py-2.5 pr-4 text-right font-normal">MRR</th>
            <th class="py-2.5 pr-4 text-right font-normal">Open invoices</th>
            <th class="py-2.5 text-right font-normal">Credit</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in teams.data || []" :key="t.team" class="border-b border-outline-gray-1">
            <td class="py-3 pr-4 font-medium text-ink-gray-8">{{ t.team }}</td>
            <td class="py-3 pr-4"><Badge variant="subtle" :theme="standingTheme(t.standing)" :label="t.standing" /></td>
            <td class="py-3 pr-4 text-right text-ink-gray-8">{{ money(t.mrr) }}</td>
            <td class="py-3 pr-4 text-right text-ink-gray-7">{{ t.open_invoices }}</td>
            <td class="py-3 text-right text-ink-gray-7">{{ money(t.credit_balance) }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>
<script setup>
import { computed } from 'vue';
import { Badge, createResource } from 'frappe-ui';
import { money, standingTheme } from '../utils';
const m = createResource({ url: 'press_billing.admin.get_metrics', auto: true });
const s = createResource({ url: 'press_billing.admin.get_summary', auto: true });
const teams = createResource({ url: 'press_billing.admin.list_teams', auto: true });
const stats = computed(() => [
  { label: 'MRR', value: money(m.data?.mrr) },
  { label: 'Teams', value: m.data?.team_count ?? 0, sub: `${m.data?.paying_on_time ?? 0} on time` },
  { label: 'Delinquent', value: m.data?.delinquent ?? 0, sub: `${m.data?.suspended ?? 0} suspended`, cls: 'text-ink-amber-3' },
  { label: 'Payment failures', value: m.data?.payment_failures ?? 0, cls: 'text-ink-red-3' },
]);
</script>
