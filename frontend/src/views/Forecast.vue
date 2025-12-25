<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-content">
        <h2 class="title">趋势预测 <span class="subtitle">AI 线性回归模型</span></h2>
        <p class="desc">基于历史销售数据的时序分析，智能推演未来营收趋势。</p>
      </div>
      
      <div class="control-bar">
        <div class="input-group">
          <label class="label">预测周期 (月)</label>
          <div class="input-wrapper">
            <input type="number" min="1" max="24" v-model.number="months" class="clean-input" />
            <span class="suffix">个月</span>
          </div>
        </div>
        <button class="primary" @click="run" :disabled="loading">
          {{ loading ? '计算模型中...' : '生成预测报告' }}
        </button>
      </div>
    </header>

    <div class="forecast-content">
      <!-- 图表区域 -->
      <div class="chart-viz-panel" :class="{ 'has-data': chartData.length }">
        <div class="viz-header" v-if="chartData.length">
          <div class="legend-group">
            <div class="legend-item"><span class="dot solid"></span>历史数据</div>
            <div class="legend-item"><span class="dot dashed"></span>AI 预测</div>
          </div>
        </div>
        
        <div ref="chartRef" class="chart-canvas"></div>
        
        <!-- Loading 遮罩 -->
        <div v-if="loading" class="overlay-mask">
          <div class="spinner large"></div>
          <span class="loading-text">正在分析时序模式...</span>
        </div>

        <!-- 空状态提示 -->
        <div v-if="!chartData.length && !loading" class="empty-hint">
          <div class="hint-icon">📈</div>
          <p>设置预测时长并开始生成</p>
        </div>
      </div>

      <!-- 智能分析卡片 -->
      <Transition name="slide-up">
        <div class="insight-card" v-if="summary">
          <div class="insight-header">
            <span class="icon">✨</span>
            <span class="insight-title">AI 智能分析摘要</span>
          </div>
          <div class="insight-body">
            <p>{{ summary }}</p>
          </div>
        </div>
      </Transition>

      <Transition name="fade">
        <div class="model-card" v-if="modelInfo.model || modelInfo.reason">
          <div class="model-row">
            <span class="model-label">使用模型</span>
            <span class="model-value">{{ modelInfo.model || '未知模型' }}</span>
          </div>
          <div class="model-row" v-if="modelInfo.reason">
            <span class="model-label">模型说明</span>
            <span class="model-value">{{ modelInfo.reason }}</span>
          </div>
        </div>
      </Transition>

      <Transition name="fade">
        <div class="model-card" v-if="longTerm.available !== undefined">
          <div class="model-row">
            <span class="model-label">长期验证</span>
            <span class="model-value">
              <span v-if="longTerm.available">留出 {{ longTerm.test_months || 12 }} 个月，可靠度 {{ longTerm.reliability || '未知' }}</span>
              <span v-else>{{ longTerm.note || '历史数据不足，无法验证长期预测。' }}</span>
            </span>
          </div>
          <div class="model-row" v-if="longTerm.available">
            <span class="model-label">验证模型</span>
            <span class="model-value">{{ longTerm.winner || '未知模型' }}</span>
          </div>
          <div class="model-row" v-if="longTerm.available">
            <span class="model-label">销售误差</span>
            <span class="model-value">{{ formatPercent(longTerm.sales_mape) }}</span>
          </div>
          <div class="model-row" v-if="longTerm.available">
            <span class="model-label">利润误差</span>
            <span class="model-value">{{ formatPercent(longTerm.profit_mape) }}</span>
          </div>
          <div class="model-row" v-if="longTerm.available">
            <span class="model-label">综合误差</span>
            <span class="model-value">{{ formatPercent(longTerm.avg_mape) }}</span>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { nextTick, onBeforeUnmount, ref } from "vue";
import http from "../api/http";
import { requestCloudSpeech } from "../api/tts";

interface SeriesPoint {
  period: string;
  sales: number;
  profit: number;
}

const months = ref(3);
const chartRef = ref<HTMLDivElement | null>(null);
const chartData = ref<SeriesPoint[]>([]);
const forecastData = ref<SeriesPoint[]>([]);
const summary = ref("");
const modelInfo = ref<{ model?: string; reason?: string }>({});
const longTerm = ref<{ available?: boolean; test_months?: number; winner?: string; sales_mape?: number; profit_mape?: number; avg_mape?: number; reliability?: string; note?: string }>({});
const loading = ref(false);
let chart: echarts.ECharts | null = null;

const initChart = () => {
  if (!chartRef.value) return;
  chart = echarts.init(chartRef.value);
  window.addEventListener('resize', () => chart?.resize());
};

const renderChart = () => {
  if (!chart) initChart();
  if (!chart) return;

  const historyPeriods = chartData.value.map((item) => item.period);
  const forecastPeriods = forecastData.value.map((item) => item.period);
  const allPeriods = [...historyPeriods, ...forecastPeriods];
  
  const salesHistory = chartData.value.map(i => i.sales);
  const salesForecast = new Array(salesHistory.length).fill(null).concat(forecastData.value.map(i => i.sales));

  const profitHistory = chartData.value.map(i => i.profit);
  const profitForecast = new Array(profitHistory.length).fill(null).concat(forecastData.value.map(i => i.profit));

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    grid: { top: 40, right: 40, bottom: 40, left: 60, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E2E8F0',
      textStyle: { color: '#333' },
      axisPointer: { type: 'cross', label: { backgroundColor: '#64748B' } },
      extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.1);'
    },
    xAxis: {
      type: 'category',
      data: allPeriods,
      axisLine: { lineStyle: { color: '#CBD5E1' } },
      axisLabel: { color: '#64748B', fontFamily: 'Inter' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: '#E2E8F0' } },
      axisLabel: { color: '#64748B' }
    },
    series: [
      {
        name: '历史销量',
        type: 'line',
        data: salesHistory,
        itemStyle: { color: '#2563EB' }, // Brand Blue
        symbol: 'none',
        smooth: true,
        lineStyle: { width: 3 }
      },
      {
        name: '历史利润',
        type: 'line',
        data: profitHistory,
        itemStyle: { color: '#059669' }, // Emerald
        symbol: 'none',
        smooth: true,
        lineStyle: { width: 3 }
      },
      {
        name: '预测销量',
        type: 'line',
        data: salesForecast,
        itemStyle: { color: '#2563EB' },
        lineStyle: { type: 'dashed', width: 2 },
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { borderWidth: 2, borderColor: '#2563EB', color: '#fff' } // 空心点
      },
      {
        name: '预测利润',
        type: 'line',
        data: profitForecast,
        itemStyle: { color: '#059669' },
        lineStyle: { type: 'dashed', width: 2 },
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { borderWidth: 2, borderColor: '#059669', color: '#fff' }
      }
    ]
  };

  chart.setOption(option);
};

const formatPercent = (value?: number) => {
  if (value === undefined || value === null || Number.isNaN(value)) return "未知";
  return `${(value * 100).toFixed(2)}%`;
};

const run = async () => {
  loading.value = true;
  try {
    const resp = await http.post("/forecast", { months: months.value });
    chartData.value = resp.data.history || [];
    forecastData.value = resp.data.forecast || [];
    summary.value = resp.data.summary || "";
    modelInfo.value = resp.data.model || {};
    longTerm.value = resp.data.long_term || {};
    await nextTick();
    renderChart();
    const speech = summary.value
      ? `趋势预测完成。${summary.value}`
      : `趋势预测完成，已生成未来${months.value}个月的预测结果。`;
    void requestCloudSpeech(speech);
  } catch (error: any) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

onBeforeUnmount(() => {
  chart?.dispose();
  window.removeEventListener('resize', () => chart?.resize());
});
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}

.title { font-size: 24px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.subtitle { font-weight: 400; color: var(--text-tertiary); font-size: 16px; margin-left: 8px; }
.desc { color: var(--text-secondary); font-size: 14px; }

.control-bar { display: flex; align-items: flex-end; gap: 24px; }

.input-group .label { display: block; font-size: 12px; color: var(--text-tertiary); margin-bottom: 8px; font-weight: 600; }

.input-wrapper {
  display: flex;
  align-items: center;
  background: var(--bg-surface);
  border: 1px solid #E2E8F0;
  border-radius: var(--radius-sm);
  padding: 0 12px;
  height: 40px;
  transition: all 0.2s;
  box-shadow: var(--shadow-xs);
}
.input-wrapper:focus-within { border-color: var(--brand-primary); box-shadow: 0 0 0 3px var(--brand-shadow); }

.clean-input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  width: 50px;
  text-align: right;
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 16px;
  outline: none;
  height: 100%;
}
.suffix { color: var(--text-tertiary); margin-left: 8px; font-size: 14px; }

/* Chart Viz */
.chart-viz-panel {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  height: 500px;
  position: relative;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
}

.viz-header {
  padding: 16px 24px;
  display: flex;
  justify-content: flex-end;
}

.legend-group { display: flex; gap: 16px; font-size: 12px; color: var(--text-secondary); }
.legend-item { display: flex; align-items: center; gap: 6px; }
.dot { width: 12px; height: 3px; border-radius: 100px; background: var(--text-secondary); }
.dot.solid { background: #2563EB; }
.dot.dashed { background: repeating-linear-gradient(90deg, #2563EB, #2563EB 4px, transparent 4px, transparent 8px); width: 20px; height: 2px; }

.chart-canvas { flex: 1; width: 100%; }

/* Insight Card */
.insight-card {
  background: #F0F9FF; /* 极淡的蓝色背景 */
  border: 1px solid #BAE6FD;
  border-radius: var(--radius-md);
  padding: 24px;
}

.insight-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.insight-title { font-size: 16px; font-weight: 600; color: #0369A1; }

.insight-body { color: #334155; font-size: 14px; line-height: 1.8; }

.model-card {
  margin-top: 16px;
  background: #fff;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  padding: 16px;
  box-shadow: var(--shadow-xs);
}

.model-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 8px;
}
.model-row:last-child { margin-bottom: 0; }
.model-label {
  width: 72px;
  color: var(--text-tertiary);
  font-size: 13px;
}
.model-value {
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.6;
}

/* Overlay */
.overlay-mask {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  color: var(--brand-primary);
}

.spinner.large {
  width: 40px;
  height: 40px;
  margin-bottom: 16px;
  border-color: rgba(37, 99, 235, 0.2);
  border-top-color: var(--brand-primary);
}

.empty-hint {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}
.hint-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; filter: grayscale(1); }
</style>
