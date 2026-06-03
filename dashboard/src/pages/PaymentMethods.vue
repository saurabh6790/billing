<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <p class="text-base font-semibold text-ink-gray-9">Cards & mandates</p>
      <Button variant="solid" theme="gray" label="Add card" @click="add = true" />
    </div>
    <div class="divide-y divide-outline-gray-1">
      <div v-for="m in methods.data || []" :key="m.name" class="flex items-center justify-between py-4">
        <div class="flex items-center gap-3">
          <component :is="m.method_type === 'card' ? LucideCreditCard : LucideSmartphone" class="size-5 text-ink-gray-5" />
          <div>
            <p class="font-medium text-ink-gray-8">{{ m.display_label || m.method_type }}
              <Badge v-if="m.is_default" theme="blue" variant="subtle" label="Default" class="ml-1" />
            </p>
            <p v-if="m.expiry_month" class="text-xs text-ink-gray-5">expires {{ m.expiry_month }}/{{ m.expiry_year }}</p>
          </div>
        </div>
        <Badge variant="subtle" :theme="m.status === 'active' ? 'green' : 'gray'" :label="m.status" />
      </div>
      <p v-if="!(methods.data || []).length" class="py-6 text-ink-gray-5">No payment methods on file.</p>
    </div>
    <AddCardDialog v-model="add" :team="team" gateway="GW-Demo-Stripe" :hasProfile="!!profile.data?.legal_name" @success="methods.reload()" />
  </div>
</template>
<script setup>
import { ref } from 'vue';
import { Badge, Button, createResource } from 'frappe-ui';
import LucideCreditCard from '~icons/lucide/credit-card';
import LucideSmartphone from '~icons/lucide/smartphone';
import AddCardDialog from '../components/AddCardDialog.vue';
const add = ref(false); const team = ref(null);
createResource({ url: 'press_billing.dashboard.whoami', auto: true, onSuccess: (d) => (team.value = d.team) });
const methods = createResource({ url: 'press_billing.dashboard.list_payment_methods', auto: true });
const profile = createResource({ url: 'press_billing.dashboard.get_billing_profile', auto: true });
</script>
