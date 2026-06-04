<template>
  <div class="rounded-xl border border-outline-gray-2 bg-surface-white p-5">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm text-ink-gray-6">{{ title }}</p>
        <p class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ money(totalBilled) }}</p>
        <p v-if="delta !== null" class="mt-1 text-xs" :class="delta >= 0 ? 'text-ink-green-3' : 'text-ink-red-3'">
          {{ delta >= 0 ? '↑' : '↓' }} {{ Math.abs(delta).toFixed(0) }}% vs last month
        </p>
      </div>
      <div class="flex items-center gap-4 text-xs text-ink-gray-6">
        <span class="flex items-center gap-1.5"><span class="size-2.5 rounded-full bg-[var(--billed)]"></span>Billed (INR equiv.)</span>
      </div>
    </div>

    <svg v-if="pts.length" :viewBox="`0 0 ${W} ${H}`" class="mt-4 w-full" :style="cssVars" preserveAspectRatio="none" style="height: 220px">
      <defs>
        <linearGradient :id="gid" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="var(--billed)" stop-opacity="0.25" />
          <stop offset="100%" stop-color="var(--billed)" stop-opacity="0" />
        </linearGradient>
      </defs>
      <!-- gridlines -->
      <g>
        <line v-for="(gy, i) in gridY" :key="i" :x1="padL" :x2="W - padR" :y1="gy.y" :y2="gy.y" stroke="currentColor" class="text-outline-gray-2" stroke-width="1" />
        <text v-for="(gy, i) in gridY" :key="'t' + i" :x="padL - 6" :y="gy.y + 3" text-anchor="end" class="fill-current text-ink-gray-4" style="font-size: 9px">{{ gy.label }}</text>
      </g>
      <!-- billed area + line -->
      <path :d="areaPath" :fill="`url(#${gid})`" />
      <polyline :points="billedLine" fill="none" stroke="var(--billed)" stroke-width="2" stroke-linejoin="round" />
      <!-- x labels -->
      <text v-for="(p, i) in pts" :key="'x' + i" :x="p.x" :y="H - 6" text-anchor="middle" class="fill-current text-ink-gray-4" style="font-size: 9px">{{ p.label }}</text>
      <!-- point markers -->
      <circle v-for="(p, i) in pts" :key="'c' + i" :cx="p.x" :cy="p.yb" r="2.5" fill="var(--billed)" />
    </svg>
    <p v-else class="mt-8 py-8 text-center text-sm text-ink-gray-5">No revenue data yet.</p>
  </div>
</template>
<script setup>
import { computed } from 'vue';
import { money } from '../utils';

const props = defineProps({ title: { type: String, default: 'Revenue' }, data: { type: Array, default: () => [] } });

const W = 720, H = 240, padL = 44, padR = 12, padT = 12, padB = 22;
const gid = `rev-grad-${Math.random().toString(36).slice(2, 8)}`;
// frappe-ui ink tokens resolved to concrete colours for the SVG strokes.
const cssVars = { '--billed': '#2570eb', '--collected': '#30a66d' };

const rows = computed(() => props.data || []);
const maxV = computed(() => Math.max(1, ...rows.value.flatMap((r) => [r.billed, r.collected])));

const niceMax = computed(() => {
  const m = maxV.value;
  const pow = Math.pow(10, Math.floor(Math.log10(m)));
  return Math.ceil(m / pow) * pow;
});

const yOf = (v) => padT + (H - padT - padB) * (1 - v / niceMax.value);
const xStep = computed(() => (W - padL - padR) / Math.max(1, rows.value.length - 1 || 1));

const pts = computed(() =>
  rows.value.map((r, i) => ({
    label: r.label,
    x: rows.value.length === 1 ? (padL + (W - padL - padR) / 2) : padL + i * xStep.value,
    yb: yOf(r.billed),
    yc: yOf(r.collected),
  })),
);

const gridY = computed(() => {
  const steps = [0, 0.5, 1];
  return steps.map((s) => ({ y: yOf(niceMax.value * s), label: kfmt(niceMax.value * s) }));
});

const billedLine = computed(() => pts.value.map((p) => `${p.x},${p.yb}`).join(' '));
const collectedLine = computed(() => pts.value.map((p) => `${p.x},${p.yc}`).join(' '));
const areaPath = computed(() => {
  if (!pts.value.length) return '';
  const top = pts.value.map((p) => `${p.x},${p.yb}`).join(' L ');
  const first = pts.value[0], last = pts.value[pts.value.length - 1];
  return `M ${first.x},${H - padB} L ${top} L ${last.x},${H - padB} Z`;
});

const totalBilled = computed(() => rows.value.reduce((s, r) => s + (r.billed || 0), 0));
const delta = computed(() => {
  const n = rows.value.length;
  if (n < 2) return null;
  const cur = rows.value[n - 1].billed, prev = rows.value[n - 2].billed;
  if (!prev) return null;
  return ((cur - prev) / prev) * 100;
});

function kfmt(v) {
  if (v >= 1e7) return '₹' + (v / 1e7).toFixed(1) + 'Cr';
  if (v >= 1e5) return '₹' + (v / 1e5).toFixed(1) + 'L';
  if (v >= 1e3) return '₹' + (v / 1e3).toFixed(0) + 'k';
  return '₹' + v;
}
</script>
