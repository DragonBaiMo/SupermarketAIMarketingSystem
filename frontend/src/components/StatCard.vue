<template>
  <div class="stat-card">
    <div class="card-main">
      <div class="header">
        <h3 class="title">{{ title }}</h3>
        <div class="icon-watermark">
          <slot name="icon"></slot>
        </div>
      </div>
      
      <div class="number-area">
        <span class="value">{{ value }}</span>
        <span v-if="unit" class="unit">{{ unit }}</span>
      </div>
    </div>

    <div class="card-footer" v-if="trend !== undefined || note">
      <div v-if="trend !== undefined" class="trend-pill" :class="trend >= 0 ? 'up' : 'down'">
        <svg v-if="trend >= 0" class="trend-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
        <svg v-else class="trend-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>
        <span class="trend-val">{{ Math.abs(trend) }}%</span>
        <span class="trend-label">较上周</span>
      </div>
      <div v-if="note" class="meta-note">{{ note }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ 
  title: string; 
  value: string | number; 
  unit?: string;
  note?: string;
  trend?: number; 
}>();
</script>

<style scoped>
.stat-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 24px;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s var(--ease-smooth);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  height: 100%;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(37, 99, 235, 0.1); /* 微蓝边框 */
}

.header {
  position: relative;
  z-index: 2;
  margin-bottom: 12px;
}

.title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  margin: 0;
}

.icon-watermark {
  position: absolute;
  top: -4px;
  right: 0;
  color: var(--text-tertiary);
  opacity: 0.15;
  transform: scale(1.2);
  pointer-events: none;
}
.icon-watermark :deep(svg) { width: 24px; height: 24px; }

.number-area {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 16px;
  z-index: 2;
}

.value {
  font-size: 32px; /* 巨大清晰 */
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums; /* 数字对齐 */
}

.unit {
  font-size: 14px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.card-footer {
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
}

.trend-icon { width: 10px; height: 10px; }

/* 涨跌颜色：清新的红绿 */
.trend-pill.up {
  background: #ECFDF5;
  color: #059669;
}
.trend-pill.down {
  background: #FEF2F2;
  color: #DC2626;
}

.trend-label {
  color: var(--text-tertiary);
  font-weight: 400;
  margin-left: 4px;
}

.meta-note {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>