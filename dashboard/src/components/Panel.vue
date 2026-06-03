<template>
  <section>
    <h2 class="mb-2 text-base font-semibold text-ink-gray-9">{{ title }}</h2>
    <table class="w-full text-sm">
      <thead><tr class="border-b border-outline-gray-2 text-left text-ink-gray-5">
        <th v-for="(c,i) in cols" :key="c" class="py-2 pr-4 font-normal" :class="i>0 ? 'text-right' : ''">{{ c }}</th>
      </tr></thead>
      <tbody>
        <tr v-for="(r,ri) in rows || []" :key="ri" class="border-b border-outline-gray-1">
          <td v-for="(f,i) in fields" :key="f" class="py-2 pr-4 text-ink-gray-8" :class="i>0 ? 'text-right' : ''">
            {{ f === moneyField ? money(r[f]) : r[f] }}
          </td>
        </tr>
        <tr v-if="!(rows || []).length"><td :colspan="cols.length" class="py-3 text-ink-gray-5">None.</td></tr>
      </tbody>
    </table>
  </section>
</template>
<script setup>
import { money } from '../utils';
defineProps({ title: String, rows: Array, cols: Array, fields: Array, moneyField: String });
</script>
