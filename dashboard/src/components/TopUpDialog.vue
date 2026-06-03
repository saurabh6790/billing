<template>
  <Dialog v-model="show" :options="{ title: 'Add credit', size: 'xl' }">
    <template #body-content>
      <div class="space-y-4">
        <p class="text-sm text-ink-gray-6">Current balance: <span class="font-medium text-ink-gray-9">{{ money(balance) }}</span></p>
        <div class="flex flex-wrap gap-2">
          <Button v-for="q in quick" :key="q" :variant="amount == q ? 'solid' : 'subtle'" theme="gray" @click="amount = q">{{ money(q) }}</Button>
        </div>
        <FormControl type="number" label="Amount (₹)" v-model="amount" />
        <FormControl type="select" label="Pay with" v-model="method" :options="methodOptions" />
        <div v-if="!hasProfile">
          <p class="mb-2 text-sm font-medium text-ink-gray-8">Billing details</p>
          <BillingFields :fields="form" />
        </div>
        <ErrorMessage :message="error" />
      </div>
    </template>
    <template #actions>
      <Button variant="solid" theme="gray" :loading="loading" @click="submit">Pay {{ money(amount) }}</Button>
    </template>
  </Dialog>
</template>
<script setup>
import { reactive, ref, computed } from 'vue';
import { Dialog, Button, FormControl, ErrorMessage, createResource } from 'frappe-ui';
import BillingFields from './BillingFields.vue';
import { money } from '../utils';
const props = defineProps({ modelValue: Boolean, team: String, balance: Number, methods: Array, hasProfile: Boolean });
const emit = defineEmits(['update:modelValue', 'success']);
const show = computed({ get: () => props.modelValue, set: (v) => emit('update:modelValue', v) });
const quick = [1000, 2000, 5000, 10000];
const amount = ref(5000); const method = ref(null);
const form = reactive({ legal_name: '', gstin: '', email: '', phone: '', address_line1: '', city: '', state: '', pincode: '' });
const error = ref(''); const loading = ref(false);
const methodOptions = computed(() => [{ label: 'Add new card', value: '' }, ...(props.methods || []).map((m) => ({ label: m.display_label || m.method_type, value: m.name }))]);
const saveProfile = createResource({ url: 'press_billing.dashboard.save_billing_profile' });
const res = createResource({ url: 'press_billing.dashboard.purchase_credits' });
async function submit() {
  error.value = ''; loading.value = true;
  try {
    if (!props.hasProfile) await saveProfile.submit({ team: props.team, ...form });
    await res.submit({ team: props.team, amount: amount.value, payment_method: method.value || null });
    emit('success'); show.value = false;
  } catch (e) { error.value = e.messages?.[0] || String(e); } finally { loading.value = false; }
}
</script>
