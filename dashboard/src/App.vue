<template>
  <div class="min-h-screen bg-surface-white text-ink-gray-9">
    <div class="mx-auto max-w-6xl px-8 py-6">
      <h1 class="text-2xl font-semibold text-ink-gray-9">Billing</h1>
      <nav class="mt-4 flex gap-6 border-b border-outline-gray-2">
        <router-link v-for="t in visible" :key="t.to" :to="t.to"
          class="-mb-px border-b-2 border-transparent px-0.5 pb-3 text-sm text-ink-gray-6 hover:text-ink-gray-8"
          exact-active-class="!border-ink-gray-9 !text-ink-gray-9 font-medium">
          {{ t.label }}
        </router-link>
      </nav>
      <div class="py-6"><router-view /></div>
    </div>
  </div>
</template>
<script setup>
import { reactive, computed } from 'vue';
import { createResource } from 'frappe-ui';
const me = reactive({ team: null, is_billing_admin: false });
createResource({ url: 'press_billing.dashboard.whoami', auto: true, onSuccess: (d) => Object.assign(me, d) });
const tabs = [
  { label: 'Overview', to: '/billing' },
  { label: 'Invoices', to: '/billing/invoices' },
  { label: 'Balances', to: '/billing/credits' },
  { label: 'Payment Methods', to: '/billing/methods' },
  { label: 'Admin', to: '/billing/admin', admin: true },
];
const visible = computed(() => tabs.filter((t) => !t.admin || me.is_billing_admin));
</script>
