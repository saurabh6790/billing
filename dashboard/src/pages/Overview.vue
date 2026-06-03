<template>
  <div class="space-y-8">
    <!-- Recurring charges / this month -->
    <div class="rounded-lg border border-outline-gray-2 px-5 py-4">
      <p class="text-lg font-semibold text-ink-gray-9">This Month</p>
      <p class="mt-1 text-sm text-ink-gray-6">Next charge date — {{ forecast.data?.period_end || '—' }}</p>
      <div class="mt-3 flex items-center justify-between">
        <p class="text-sm text-ink-gray-7">Projected amount so far is
          <span class="font-medium text-ink-gray-9">{{ money(forecast.data?.projected_total) }}</span>
        </p>
        <Button label="View Invoices" @click="$router.push('/billing/invoices')" />
      </div>
    </div>

    <!-- Payment details -->
    <section>
      <h2 class="mb-1 text-base font-semibold text-ink-gray-9">Payment details</h2>
      <div>
        <DetailRow label="Active card">
          <template #desc>
            <span v-if="defaultCard">{{ defaultCard.display_label }}<span v-if="defaultCard.expiry_month"> · exp {{ defaultCard.expiry_month }}/{{ defaultCard.expiry_year }}</span></span>
            <span v-else>No card on file</span>
          </template>
          <template #action><Button :label="defaultCard ? 'Change card' : 'Add card'" @click="addCard = true" /></template>
        </DetailRow>

        <DetailRow label="Billing address">
          <template #desc>
            <span v-if="profile.data?.legal_name">{{ profile.data.legal_name }}<span v-if="profile.data.address_line1">, {{ profile.data.address_line1 }}</span><span v-if="profile.data.city">, {{ profile.data.city }}</span><span v-if="profile.data.gstin"> · GSTIN {{ profile.data.gstin }}</span></span>
            <span v-else>Not added yet</span>
          </template>
          <template #action><Button label="Edit" @click="editAddr = true" /></template>
        </DetailRow>

        <DetailRow label="Mode of payment">
          <template #desc>{{ mode === 'prepaid' ? 'Drawn from your prepaid wallet' : 'Your card will be charged for monthly usage' }}</template>
          <template #action>
            <FormControl type="select" v-model="mode" :options="[{label:'Card (postpaid)',value:'postpaid'},{label:'Prepaid Credits',value:'prepaid'}]" @change="saveMode" />
          </template>
        </DetailRow>

        <DetailRow label="Credit balance">
          <template #desc>{{ money(balance.data?.balance) }}</template>
          <template #action><Button label="+ Add credit" @click="topup = true" /></template>
        </DetailRow>

        <DetailRow label="Budget alert">
          <template #desc>Receive an email alert if the projected month-end total exceeds a limit.</template>
          <template #action><Button label="Set Budget Alert" @click="$router.push('/billing/methods')" /></template>
        </DetailRow>
      </div>
    </section>

    <AddCardDialog v-model="addCard" :team="team" gateway="GW-Demo-Stripe" @success="methods.reload()" />
    <TopUpDialog v-model="topup" :team="team" :balance="balance.data?.balance" :methods="methods.data" :hasProfile="!!profile.data?.legal_name" @success="() => { balance.reload(); forecast.reload(); }" />
    <BillingAddressDialog v-model="editAddr" :team="team" :profile="profile.data" @success="profile.reload()" />
  </div>
</template>
<script setup>
import { ref, computed } from 'vue';
import { Button, FormControl, createResource } from 'frappe-ui';
import DetailRow from '../components/DetailRow.vue';
import AddCardDialog from '../components/AddCardDialog.vue';
import TopUpDialog from '../components/TopUpDialog.vue';
import BillingAddressDialog from '../components/BillingAddressDialog.vue';
import { money } from '../utils';
const team = ref(null); const mode = ref('postpaid');
const addCard = ref(false); const topup = ref(false); const editAddr = ref(false);
createResource({ url: 'press_billing.dashboard.whoami', auto: true, onSuccess: (d) => (team.value = d.team) });
const forecast = createResource({ url: 'press_billing.dashboard.get_forecast', auto: true });
const balance = createResource({ url: 'press_billing.dashboard.get_credit_balance', auto: true });
const methods = createResource({ url: 'press_billing.dashboard.list_payment_methods', auto: true });
const profile = createResource({ url: 'press_billing.dashboard.get_billing_profile', auto: true });
const settings = createResource({ url: 'press_billing.dashboard.get_billing_settings', auto: true, onSuccess: (d) => (mode.value = d.billing_mode || 'postpaid') });
const saveSettings = createResource({ url: 'press_billing.dashboard.save_billing_settings' });
const defaultCard = computed(() => (methods.data || []).find((m) => m.method_type === 'card' && m.is_default) || (methods.data || [])[0]);
function saveMode() { saveSettings.submit({ team: team.value, billing_mode: mode.value }); }
</script>
