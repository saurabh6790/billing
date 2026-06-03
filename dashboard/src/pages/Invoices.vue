<template>
  <div>
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-outline-gray-2 text-left text-ink-gray-5">
          <th class="py-2.5 pr-4 font-normal">Invoice</th>
          <th class="py-2.5 pr-4 font-normal">Status</th>
          <th class="py-2.5 pr-4 font-normal">Date</th>
          <th class="py-2.5 pr-4 text-right font-normal">Total</th>
          <th class="py-2.5 pr-4 text-right font-normal">Amount Paid</th>
          <th class="py-2.5 pr-4 text-right font-normal">Amount Due</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="inv in invoices.data || []" :key="inv.name" class="border-b border-outline-gray-1">
          <td class="py-3 pr-4 font-medium text-ink-gray-8">{{ inv.name }}</td>
          <td class="py-3 pr-4"><Badge variant="subtle" :theme="statusTheme(inv.status)" :label="inv.status" /></td>
          <td class="py-3 pr-4 text-ink-gray-7">{{ inv.period_start }} – {{ inv.period_end }}</td>
          <td class="py-3 pr-4 text-right text-ink-gray-8">{{ money(inv.total) }}</td>
          <td class="py-3 pr-4 text-right text-ink-gray-8">{{ money(inv.amount_paid) }}</td>
          <td class="py-3 pr-4 text-right text-ink-gray-8">{{ money(inv.total - inv.amount_paid) }}</td>
          <td class="py-3 text-right"><Button v-if="inv.status !== 'Draft'" label="Download Invoice" /></td>
        </tr>
        <tr v-if="!(invoices.data || []).length"><td colspan="7" class="py-6 text-ink-gray-5">No invoices yet.</td></tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { Badge, Button, createResource } from 'frappe-ui';
import { money, statusTheme } from '../utils';
const invoices = createResource({ url: 'press_billing.dashboard.list_invoices', auto: true });
</script>
