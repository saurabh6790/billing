<template>
  <Dialog v-model="show" :options="{ title: 'Add a card', size: 'xl' }">
    <template #body-content>
      <div class="space-y-4">
        <div class="rounded-md bg-surface-gray-2 px-3 py-2 text-xs text-ink-gray-6">
          In production the card number is entered in the gateway's secure (PCI) field and tokenised client-side. This demo records the display details.
        </div>
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <FormControl class="sm:col-span-3" type="text" label="Cardholder / label" v-model="label" placeholder="Visa ····4242" />
          <FormControl type="number" label="Exp. month" v-model="month" />
          <FormControl type="number" label="Exp. year" v-model="year" />
        </div>
        <div v-if="!hasProfile">
          <p class="mb-2 text-sm font-medium text-ink-gray-8">Billing details</p>
          <BillingFields :fields="form" />
        </div>
        <ErrorMessage :message="error" />
      </div>
    </template>
    <template #actions>
      <Button variant="solid" theme="gray" :loading="loading" @click="submit">Add card</Button>
    </template>
  </Dialog>
</template>
<script setup>
import { reactive, ref, computed } from 'vue';
import { Dialog, Button, FormControl, ErrorMessage, createResource } from 'frappe-ui';
import BillingFields from './BillingFields.vue';
const props = defineProps({ modelValue: Boolean, team: String, gateway: String, hasProfile: Boolean });
const emit = defineEmits(['update:modelValue', 'success']);
const show = computed({ get: () => props.modelValue, set: (v) => emit('update:modelValue', v) });
const label = ref('Visa ····4242'); const month = ref(12); const year = ref(2030);
const form = reactive({ legal_name: '', gstin: '', email: '', phone: '', address_line1: '', city: '', state: '', pincode: '' });
const error = ref(''); const loading = ref(false);
const saveProfile = createResource({ url: 'press_billing.dashboard.save_billing_profile' });
const addCard = createResource({ url: 'press_billing.dashboard.add_demo_card' });
async function submit() {
  error.value = ''; loading.value = true;
  try {
    if (!props.hasProfile) await saveProfile.submit({ team: props.team, ...form });
    await addCard.submit({ team: props.team, gateway: props.gateway, display_label: label.value, expiry_month: month.value, expiry_year: year.value });
    emit('success'); show.value = false;
  } catch (e) { error.value = e.messages?.[0] || String(e); } finally { loading.value = false; }
}
</script>
