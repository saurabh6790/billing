<template>
  <div class="flex h-screen overflow-hidden bg-surface-white text-ink-gray-9">
    <aside class="flex w-60 shrink-0 flex-col border-r border-outline-gray-2 bg-surface-gray-1">
      <div class="p-3">
        <div class="flex items-center gap-2 px-1 py-1.5">
          <div class="flex size-7 items-center justify-center rounded bg-surface-gray-5 text-xs font-bold text-ink-white">CB</div>
          <span class="text-sm font-semibold text-ink-gray-9">Cloud Billing</span>
        </div>
        <p class="mt-3 px-1 text-xs font-medium uppercase tracking-wide text-ink-gray-5">Team</p>
        <FormControl class="mt-1" type="select" :modelValue="store.team" @update:modelValue="switchTeam" :options="teamOptions" />
        <div v-if="store.isAdmin" class="mt-3 flex rounded-md bg-surface-gray-3 p-0.5">
          <button v-for="v in ['customer','admin']" :key="v" @click="setView(v)"
            class="flex-1 rounded px-2 py-1 text-xs font-medium capitalize transition"
            :class="store.view===v ? 'bg-surface-white text-ink-gray-9 shadow-sm' : 'text-ink-gray-6'">{{ v }} view</button>
        </div>
      </div>
      <nav class="flex flex-1 flex-col gap-0.5 px-3">
        <router-link v-for="it in nav" :key="it.to" :to="it.to"
          class="flex items-center gap-2.5 rounded py-1.5 px-2.5 text-sm text-ink-gray-7 transition hover:bg-surface-gray-2"
          exact-active-class="!bg-surface-white !text-ink-gray-9 shadow-sm">
          <component :is="it.icon" class="size-4 text-ink-gray-6" /><span>{{ it.label }}</span>
        </router-link>
      </nav>
      <div class="border-t border-outline-gray-2 p-3 text-xs text-ink-gray-5">{{ store.team || '—' }}</div>
    </aside>
    <main class="flex-1 overflow-auto"><div class="mx-auto max-w-5xl px-8 py-8"><router-view /></div></main>
  </div>
</template>
<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { FormControl, createResource } from 'frappe-ui';
import LucideLayoutDashboard from '~icons/lucide/layout-dashboard';
import LucideReceipt from '~icons/lucide/receipt';
import LucideCreditCard from '~icons/lucide/credit-card';
import LucideWallet from '~icons/lucide/wallet';
import LucideUsers from '~icons/lucide/users';
import LucideChartBar from '~icons/lucide/chart-bar';
import { store } from './store';
const router = useRouter();
createResource({ url: 'press_billing.dashboard.whoami', auto: true, onSuccess: (d) => { store.team = d.team; store.isAdmin = d.is_billing_admin; } });
const teams = createResource({ url: 'press_billing.dashboard.list_switchable_teams', auto: true });
const teamOptions = computed(() => (teams.data || []).map((t) => ({ label: `${t.team} (${t.tier || '—'})`, value: t.team })));
function switchTeam(t) { store.team = t; }
function setView(v) { store.view = v; router.push(v === 'admin' ? '/billing/admin' : '/billing'); }
const customerNav = [
  { label: 'Overview', to: '/billing', icon: LucideLayoutDashboard },
  { label: 'Invoices', to: '/billing/invoices', icon: LucideReceipt },
  { label: 'Credits', to: '/billing/credits', icon: LucideWallet },
  { label: 'Payment Methods', to: '/billing/methods', icon: LucideCreditCard },
];
const adminNav = [
  { label: 'Overview', to: '/billing/admin', icon: LucideLayoutDashboard },
  { label: 'Teams', to: '/billing/admin/teams', icon: LucideUsers },
  { label: 'Analytics', to: '/billing/admin/analytics', icon: LucideChartBar },
];
const nav = computed(() => (store.view === 'admin' ? adminNav : customerNav));
</script>
