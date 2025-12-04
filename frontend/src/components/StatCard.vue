<template>
  <div class="stat-card">
    <div style="font-size: 13px; color: #6b7280">{{ title }}</div>
    <div style="font-size: 26px; font-weight: 700; margin-top: 8px">{{ value }}</div>
    <div v-if="note" style="font-size: 12px; color: #9ca3af; margin-top: 4px">{{ note }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; value: string | number; note?: string }>();
</script>
