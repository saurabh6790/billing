<template>
  <div class="space-y-8">
    <!-- trust tier + standing -->
    <div class="flex flex-wrap items-center gap-x-6 gap-y-1 text-sm">
      <span class="text-ink-gray-6">Trust tier: <span class="font-medium text-ink-gray-9">{{ ov.data?.tier || '—' }}</span></span>
      <span class="text-ink-gray-6">Cap: <span class="font-medium text-ink-gray-9">{{ money(ov.data?.max_spend) }}/mo</span></span>
      <span class="text-ink-gray-6">Standing: <Badge variant="subtle" :theme="standingTheme(ov.data?.standing)" :label="titleCase(ov.data?.standing)" /></span>
      <span class="text-ink-gray-6">Resources: <span class="font-medium text-ink-gray-9">{{ ov.data?.resources ?? 0 }}</span></span>
    </div>

    <!-- credit shortfall alert (prepaid) -->
    <div v-if="forecast.data?.credit_alert" class="rounded-md border border-outline-red-1 bg-surface-red-1 px-4 py-3 text-sm text-ink-red-4">
      Your projected bill ({{ money(forecast.data.projected_total) }}) exceeds your wallet balance ({{ money(forecast.data.credit_balance) }}). Top up {{ money(forecast.data.shortfall) }} to avoid interruption.
    </div>

    <!-- this month + services -->
    <div class="rounded-lg border border-outline-gray-2 px-5 py-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-lg font-semibold text-ink-gray-9">This Month</p>
          <p class="mt-1 text-sm text-ink-gray-6">Period ends {{ forecast.data?.period_end || '—' }} · {{ forecast.data?.days_remaining ?? '—' }} days left</p>
        </div>
        <p class="text-2xl font-semibold text-ink-gray-9">{{ money(forecast.data?.projected_total) }}</p>
      </div>
      <table v-if="forecast.data?.line_items?.length" class="mt-4 w-full text-sm">
        <thead><tr class="border-b border-outline-gray-1 text-left text-ink-gray-5">
          <th class="py-1.5 pr-4 font-normal">Service</th><th class="py-1.5 pr-4 font-normal">Plan</th>
          <th class="py-1.5 pr-4 text-right font-normal">Usage</th><th class="py-1.5 text-right font-normal">Amount</th>
        </tr></thead>
        <tbody>
          <tr v-for="(li,i) in forecast.data.line_items" :key="i" class="border-b border-outline-gray-1 last:border-0">
            <td class="py-1.5 pr-4 text-ink-gray-8 capitalize">{{ li.resource_type }}</td>
            <td class="py-1.5 pr-4 text-ink-gray-7">{{ li.plan || '—' }}</td>
            <td class="py-1.5 pr-4 text-right text-ink-gray-7">{{ li.days ? li.days + ' day(s)' : li.quantity }}</td>
            <td class="py-1.5 text-right text-ink-gray-8">{{ money(li.amount) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- payment details -->
    <section>
      <h2 class="mb-1 text-base font-semibold text-ink-gray-9">Payment details</h2>
      <div>
        <DetailRow label="Mode of payment">
          <template #desc>{{ mode === 'prepaid' ? 'Drawn from your prepaid wallet' : 'Your card will be charged for monthly usage' }}</template>
          <template #action><FormControl type="select" v-model="mode" :options="[{label:'Card (postpaid)',value:'postpaid'},{label:'Prepaid Credits',value:'prepaid'}]" @change="saveMode" /></template>
        </DetailRow>

        <DetailRow v-if="mode === 'postpaid'" label="Active card">
          <template #desc><span v-if="defaultCard">{{ defaultCard.display_label }}<span v-if="defaultCard.expiry_month"> · exp {{ defaultCard.expiry_month }}/{{ defaultCard.expiry_year }}</span></span><span v-else>No payment method yet</span></template>
          <template #action><Button :label="defaultCard ? 'Manage' : 'Add'" @click="$router.push('/billing/methods')" /></template>
        </DetailRow>

        <DetailRow v-if="mode === 'prepaid'" label="Credit balance">
          <template #desc>{{ money(balance.data?.balance) }}</template>
          <template #action><Button label="+ Add credit" @click="topup = true" /></template>
        </DetailRow>

        <DetailRow label="Billing address">
          <template #desc><span v-if="profile.data?.legal_name">{{ profile.data.legal_name }}<span v-if="profile.data.city">, {{ profile.data.city }}</span><span v-if="profile.data.gstin"> · GSTIN {{ profile.data.gstin }}</span></span><span v-else>Not added yet</span></template>
          <template #action><Button label="Edit" @click="editAddr = true" /></template>
        </DetailRow>
      </div>
    </section>

    <TopUpDialog v-model="topup" :team="store.team" :balance="balance.data?.balance" :hasProfile="!!profile.data?.legal_name" @success="() => { balance.reload(); forecast.reload(); }" />
    <BillingAddressDialog v-model="editAddr" :team="store.team" :profile="profile.data" @success="profile.reload()" />
  </div>
</template>
<script setup>
import { ref, computed, watch } from 'vue';
import { Button, FormControl, Badge, createResource } from 'frappe-ui';
import { store } from '../store';
import DetailRow from '../components/DetailRow.vue';
import TopUpDialog from '../components/TopUpDialog.vue';
import BillingAddressDialog from '../components/BillingAddressDialog.vue';
import { money, titleCase, standingTheme } from '../utils';
const mk = (url) => createResource({ url, makeParams: () => ({ team: store.team }) });
const ov = mk('press_billing.dashboard.get_team_overview');
const forecast = mk('press_billing.dashboard.get_forecast');
const balance = mk('press_billing.dashboard.get_credit_balance');
const methods = mk('press_billing.dashboard.list_payment_methods');
const profile = mk('press_billing.dashboard.get_billing_profile');
const settings = mk('press_billing.dashboard.get_billing_settings');
const saveSettings = createResource({ url: 'press_billing.dashboard.save_billing_settings' });
const mode = ref('postpaid');
const topup = ref(false); const editAddr = ref(false);
watch(() => store.team, (t) => { if (t) [ov,forecast,balance,methods,profile,settings].forEach((r) => r.reload()); }, { immediate: true });
watch(() => settings.data, (d) => { if (d) mode.value = d.billing_mode || 'postpaid'; });
const defaultCard = computed(() => (methods.data || []).find((m) => m.is_default) || (methods.data || [])[0]);
function saveMode() { saveSettings.submit({ team: store.team, billing_mode: mode.value }).then(() => forecast.reload()); }
</script>
