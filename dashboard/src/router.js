import { createRouter, createWebHistory } from 'vue-router';
const routes = [
  { path: '/', redirect: '/billing' },
  { path: '/billing', name: 'Overview', component: () => import('@/pages/Overview.vue') },
  { path: '/billing/forecast', name: 'Forecast', component: () => import('@/pages/Forecast.vue') },
  { path: '/billing/invoices', name: 'Invoices', component: () => import('@/pages/Invoices.vue') },
  { path: '/billing/credits', name: 'Credits', component: () => import('@/pages/Credits.vue') },
  { path: '/billing/methods', name: 'PaymentMethods', component: () => import('@/pages/PaymentMethods.vue') },
  { path: '/billing/admin', name: 'AdminOverview', component: () => import('@/pages/AdminOverview.vue') },
  { path: '/billing/admin/teams', name: 'AdminTeams', component: () => import('@/pages/AdminTeams.vue') },
  { path: '/billing/admin/analytics', name: 'AdminAnalytics', component: () => import('@/pages/AdminAnalytics.vue') },
];
export default createRouter({ history: createWebHistory('/billing'), routes });
