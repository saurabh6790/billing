<template>
  <Dialog v-model="show" :options="{ title: 'Add payment method', size: 'xl' }">
    <template #body-content>
      <div class="space-y-4">
        <div class="rounded-md bg-surface-gray-2 px-3 py-2 text-xs text-ink-gray-6">
          Authorise a UPI Autopay mandate through Razorpay Checkout. The mandate ceiling equals your trust-tier cap; your bank approves it — we never see the instrument.
        </div>
        <div v-if="!hasProfile">
          <p class="mb-2 text-sm font-medium text-ink-gray-8">Billing details</p>
          <BillingFields :fields="form" />
        </div>
        <ErrorMessage :message="error" />
      </div>
    </template>
    <template #actions>
      <Button variant="solid" theme="gray" :loading="loading" @click="submit">Set up with Razorpay</Button>
    </template>
  </Dialog>
</template>
<script setup>
import { reactive, ref, computed } from 'vue';
import { Dialog, Button, ErrorMessage, createResource } from 'frappe-ui';
import BillingFields from './BillingFields.vue';
import { openRazorpay } from '../utils';
const props = defineProps({ modelValue: Boolean, team: String, hasProfile: Boolean });
const emit = defineEmits(['update:modelValue', 'success']);
const show = computed({ get: () => props.modelValue, set: (v) => emit('update:modelValue', v) });
const form = reactive({ legal_name: '', gstin: '', email: '', phone: '', address_line1: '', city: '', state: '', pincode: '' });
const error = ref(''); const loading = ref(false);
const saveProfile = createResource({ url: 'press_billing.dashboard.save_billing_profile' });
const setup = createResource({ url: 'press_billing.dashboard.setup_payment_method_order' });
const confirm = createResource({ url: 'press_billing.dashboard.confirm_payment_method_order' });
async function submit() {
  error.value = ''; loading.value = true;
  try {
    if (!props.hasProfile) await saveProfile.submit({ team: props.team, ...form });
    const order = await setup.submit({ team: props.team });
    const resp = await openRazorpay({ key: order.key_id, order_id: order.order_id, amount: order.amount || 100,
      description: 'UPI Autopay mandate', prefill: { name: form.legal_name, email: form.email } });
    await confirm.submit({ payment_method: order.payment_method, razorpay_payment_id: resp.razorpay_payment_id,
      razorpay_order_id: resp.razorpay_order_id, razorpay_signature: resp.razorpay_signature, razorpay_token_id: resp.razorpay_payment_id });
    emit('success'); show.value = false;
  } catch (e) { error.value = e.messages?.[0] || e.message || String(e); } finally { loading.value = false; }
}
</script>
