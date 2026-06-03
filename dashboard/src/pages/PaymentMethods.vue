<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <p class="text-base font-semibold text-ink-gray-9">Cards & mandates</p>
      <Button variant="solid" theme="gray" label="Add payment method" @click="add = true" />
    </div>
    <div class="divide-y divide-outline-gray-1">
      <div v-for="m in methods.data || []" :key="m.name" class="flex items-center justify-between py-4">
        <div class="flex items-center gap-3">
          <component :is="m.method_type === 'card' ? LucideCreditCard : LucideSmartphone" class="size-5 text-ink-gray-5" />
          <div>
            <p class="font-medium text-ink-gray-8">{{ m.display_label || m.method_type }}<Badge v-if="m.is_default" theme="blue" variant="subtle" label="Default" class="ml-1" /></p>
            <p v-if="m.expiry_month" class="text-xs text-ink-gray-5">expires {{ m.expiry_month }}/{{ m.expiry_year }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <Button v-if="!m.is_default && m.status==='active'" label="Make default" @click="makeDefault(m.name)" />
          <Button v-if="!m.is_default" theme="red" variant="subtle" label="Remove" @click="remove(m.name)" />
        </div>
      </div>
      <p v-if="!(methods.data || []).length" class="py-6 text-ink-gray-5">No payment methods on file.</p>
    </div>
    <AddCardDialog v-model="add" :team="store.team" :hasProfile="!!profile.data?.legal_name" @success="methods.reload()" />
  </div>
</template>
<script setup>
import { ref, watch } from 'vue';
import { Badge, Button, createResource } from 'frappe-ui';
import LucideCreditCard from '~icons/lucide/credit-card';
import LucideSmartphone from '~icons/lucide/smartphone';
import { store } from '../store';
import AddCardDialog from '../components/AddCardDialog.vue';
const add = ref(false);
const methods = createResource({ url: 'press_billing.dashboard.list_payment_methods', makeParams: () => ({ team: store.team }) });
const profile = createResource({ url: 'press_billing.dashboard.get_billing_profile', makeParams: () => ({ team: store.team }) });
watch(() => store.team, (t) => { if (t) { methods.reload(); profile.reload(); } }, { immediate: true });
const removeRes = createResource({ url: 'press_billing.dashboard.remove_payment_method', onSuccess: () => methods.reload() });
const defaultRes = createResource({ url: 'press_billing.dashboard.set_default_payment_method', onSuccess: () => methods.reload() });
function remove(name) { removeRes.submit({ payment_method: name }); }
function makeDefault(name) { defaultRes.submit({ payment_method: name }); }
</script>
