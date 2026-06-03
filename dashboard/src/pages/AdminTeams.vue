<template>
  <div>
    <table class="w-full text-sm">
      <thead><tr class="border-b border-outline-gray-2 text-left text-ink-gray-5">
        <th class="py-2.5 pr-4 font-normal">Team</th><th class="py-2.5 pr-4 font-normal">Tier</th>
        <th class="py-2.5 pr-4 font-normal">Standing</th><th class="py-2.5 pr-4 text-right font-normal">Resources</th>
        <th class="py-2.5 pr-4 text-right font-normal">MRR</th><th class="py-2.5 pr-4 text-right font-normal">Invoices</th><th class="py-2.5 text-right font-normal">Credit</th>
      </tr></thead>
      <tbody>
        <tr v-for="t in teams.data || []" :key="t.team" class="cursor-pointer border-b border-outline-gray-1 hover:bg-surface-gray-1" @click="open(t)">
          <td class="py-3 pr-4 font-medium text-ink-gray-8">{{ t.team }}</td>
          <td class="py-3 pr-4 text-ink-gray-7">{{ t.tier }}</td>
          <td class="py-3 pr-4"><Badge variant="subtle" :theme="standingTheme(t.standing)" :label="titleCase(t.standing)" /></td>
          <td class="py-3 pr-4 text-right text-ink-gray-7">{{ t.resources }}</td>
          <td class="py-3 pr-4 text-right text-ink-gray-8">{{ money(t.mrr) }}</td>
          <td class="py-3 pr-4 text-right text-ink-gray-7">{{ t.invoices }}<span v-if="t.open_invoices" class="text-ink-amber-3"> ({{ t.open_invoices }} open)</span></td>
          <td class="py-3 text-right text-ink-gray-7">{{ money(t.credit_balance) }}</td>
        </tr>
      </tbody>
    </table>
    <TeamDetailDialog v-model="show" :data="selected" />
  </div>
</template>
<script setup>
import { ref } from 'vue';
import { Badge, createResource } from 'frappe-ui';
import TeamDetailDialog from '../components/TeamDetailDialog.vue';
import { money, titleCase, standingTheme } from '../utils';
const teams = createResource({ url: 'press_billing.admin.list_teams', auto: true });
const show = ref(false); const selected = ref(null);
function open(t) { selected.value = t; show.value = true; }
</script>
