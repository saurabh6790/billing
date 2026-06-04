<template>
  <div class="rounded-xl border border-outline-gray-2 bg-surface-white p-5">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm text-ink-gray-6">{{ title }}</p>
        <p class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ money(total) }}</p>
        <p class="mt-1 text-xs text-ink-gray-5">{{ subtitle }}</p>
      </div>
    </div>
    <svg v-if="rows.length" :viewBox="`0 0 ${W} ${H}`" class="mt-4 w-full" preserveAspectRatio="none" style="height: 200px">
      <g>
        <line v-for="(gy, i) in gridY" :key="i" :x1="padL" :x2="W - padR" :y1="gy.y" :y2="gy.y" stroke="currentColor" class="text-outline-gray-2" stroke-width="1" />
        <text v-for="(gy, i) in gridY" :key="'t' + i" :x="padL - 6" :y="gy.y + 3" text-anchor="end" class="fill-current text-ink-gray-4" style="font-size: 9px">{{ gy.label }}</text>
      </g>
      <g v-for="(b, i) in bars" :key="i">
        <rect :x="b.x" :y="b.y" :width="b.w" :height="b.h" rx="2" fill="#30a66d" />
        <text :x="b.cx" :y="H - 6" text-anchor="middle" class="fill-current text-ink-gray-4" style="font-size: 9px">{{ b.label }}</text>
      </g>
    </svg>
    <p v-else class="mt-8 py-8 text-center text-sm text-ink-gray-5">No data yet.</p>
  </div>
</template>
<script setup>
import { computed } from 'vue';
import { money } from '../utils';

const props = defineProps({
  title: { type: String, default: 'Payments' },
  subtitle: { type: String, default: '' },
  data: { type: Array, default: () => [] },
  field: { type: String, default: 'collected' },
});

const W = 720, H = 220, padL = 44, padR = 12, padT = 12, padB = 22;
const rows = computed(() => props.data || []);
const maxV = computed(() => Math.max(1, ...rows.value.map((r) => r[props.field] || 0)));
const niceMax = computed(() => {
  const m = maxV.value, pow = Math.pow(10, Math.floor(Math.log10(m)));
  return Math.ceil(m / pow) * pow;
});
const yOf = (v) => padT + (H - padT - padB) * (1 - v / niceMax.value);
const slot = computed(() => (W - padL - padR) / Math.max(1, rows.value.length));
const bars = computed(() =>
  rows.value.map((r, i) => {
    const w = slot.value * 0.6;
    const x = padL + i * slot.value + (slot.value - w) / 2;
    const y = yOf(r[props.field] || 0);
    return { x, y, w, h: Math.max(0, H - padB - y), cx: x + w / 2, label: r.label };
  }),
);
const gridY = computed(() => [0, 0.5, 1].map((s) => ({ y: yOf(niceMax.value * s), label: kfmt(niceMax.value * s) })));
const total = computed(() => rows.value.reduce((s, r) => s + (r[props.field] || 0), 0));

function kfmt(v) {
  if (v >= 1e7) return '₹' + (v / 1e7).toFixed(1) + 'Cr';
  if (v >= 1e5) return '₹' + (v / 1e5).toFixed(1) + 'L';
  if (v >= 1e3) return '₹' + (v / 1e3).toFixed(0) + 'k';
  return '₹' + v;
}
</script>
