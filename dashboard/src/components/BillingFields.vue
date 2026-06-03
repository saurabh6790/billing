<template>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
    <FormControl type="text" label="Legal name" v-model="fields.legal_name" />
    <FormControl type="text" label="GSTIN" v-model="fields.gstin" placeholder="27AAPFU0939F1ZV" />
    <FormControl type="text" label="Billing email" v-model="fields.email" />
    <FormControl type="text" label="Phone" v-model="fields.phone" />
    <FormControl type="text" label="Address" v-model="fields.address_line1" class="sm:col-span-2" />
    <FormControl type="text" label="City" v-model="fields.city" />
    <FormControl type="text" label="State" v-model="fields.state" />
    <FormControl type="text" label="Pincode" v-model="fields.pincode" />
  </div>
</template>
<script setup>
import { FormControl } from 'frappe-ui';
defineProps({ fields: Object });
</script>
