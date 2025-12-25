<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-content">
        <h2 class="title">客群透视 <span class="subtitle">RFM 聚类模型</span></h2>
        <p class="desc">基于消费近度 (R)、频率 (F)、金额 (M) 的 K-Means 智能分层分析。</p>
      </div>
      
      <div class="control-bar">
        <div class="stepper-group">
          <span class="label">聚类数量 (K值)</span>
          <div class="stepper">
            <button @click="k > 2 && k--" :disabled="k <= 2" class="step-btn">－</button>
            <span class="step-val">{{ k }}</span>
            <button @click="k < 10 && k++" :disabled="k >= 10" class="step-btn">＋</button>
          </div>
        </div>
        <button class="primary" @click="run" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '运算中...' : '开始分析' }}
        </button>
      </div>
    </header>

    <Transition name="fade">
      <div class="analysis-layout" v-if="summary.length">
        <!-- 雷达图面板 -->
        <div class="card-panel chart-panel">
          <div class="panel-header">
            <h3 class="panel-title">群组特征雷达</h3>
          </div>
          <div ref="chartRef" class="chart-canvas"></div>
        </div>

        <!-- 数据明细面板 -->
        <div class="card-panel table-panel">
          <div class="panel-header">
            <h3 class="panel-title">分群详细数据</h3>
            <button class="secondary small" @click="exportData">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              导出 CSV
            </button>
          </div>
          
          <div class="table-scroll">
            <table class="modern-table">
              <thead>
                <tr>
                  <th>群组编号</th>
                  <th class="text-right">规模 (人)</th>
                  <th class="text-right">最近购买 (天)</th>
                  <th class="text-right">购买频率 (次)</th>
                  <th class="text-right">消费金额 (元)</th>
                  <th>AI 智能标签</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in summary" :key="item.cluster">
                  <td>
                    <span class="cluster-badge" :style="{ '--badge-color': colorPalette[index % colorPalette.length] }">
                      Group {{ item.cluster }}
                    </span>
                  </td>
                  <td class="text-right font-mono">{{ item.count }}</td>
                  <td class="text-right font-mono">{{ item.R_mean?.toFixed(1) }}</td>
                  <td class="text-right font-mono">{{ item.F_mean?.toFixed(1) }}</td>
                  <td class="text-right font-mono bold">{{ formatMoney(item.M_mean) }}</td>
                  <td>
                    <span class="tag-label">{{ item.label || '未定义' }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 4"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path><path d="M2 12h20"></path></svg>
        </div>
        <p>请调整 K 值并点击“开始分析”以生成报告。</p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { nextTick, onBeforeUnmount, ref } from "vue";
import http from "../api/http";
import { requestCloudSpeech } from "../api/tts";

interface ClusterSummary {
  cluster: number;
  count: number;
  R_mean: number;
  F_mean: number;
  M_mean: number;
  label: string;
}

const k = ref(4);
const summary = ref<ClusterSummary[]>([]);
const chartRef = ref<HTMLDivElement | null>(null);
const loading = ref(false);
let chart: echarts.ECharts | null = null;

// 清新的色彩系统
const colorPalette = ['#3B82F6', '#10B981', '#F59E0B', '#EC4899', '#8B5CF6', '#06B6D4'];

const formatMoney = (val: number) => new Intl.NumberFormat('zh-CN').format(Math.round(val));

const renderChart = () => {
  if (!chartRef.value || !summary.value.length) return;
  if (!chart) {
    chart = echarts.init(chartRef.value);
    window.addEventListener('resize', () => chart?.resize());
  }

  const maxR = Math.max(...summary.value.map(s => s.R_mean)) * 1.1;
  const maxF = Math.max(...summary.value.map(s => s.F_mean)) * 1.1;
  const maxM = Math.max(...summary.value.map(s => s.M_mean)) * 1.1;

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    radar: {
      indicator: [
        { name: '最近购买 (R)', max: maxR },
        { name: '购买频率 (F)', max: maxF },
        { name: '消费金额 (M)', max: maxM }
      ],
      radius: '65%',
      splitNumber: 4,
      axisName: { color: '#64748B', fontWeight: 'bold' }, //  Slate-500
      splitLine: {
        lineStyle: { color: '#E2E8F0' }
      },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: '#E2E8F0' } }
    },
    series: [
      {
        type: 'radar',
        data: summary.value.map((s, index) => ({
          value: [s.R_mean, s.F_mean, s.M_mean],
          name: `Group ${s.cluster}`,
          itemStyle: { color: colorPalette[index % colorPalette.length] },
          areaStyle: { opacity: 0.2 },
          lineStyle: { width: 2 }
        }))
      }
    ]
  };

  chart.setOption(option);
};

const run = async () => {
  loading.value = true;
  try {
    const resp = await http.post("/clustering", { k: k.value });
    summary.value = resp.data.summary || [];
    await nextTick();
    renderChart();
    if (summary.value.length) {
      const labels = summary.value
        .slice(0, 3)
        .map((item) => item.label || "未定义")
        .join("、");
      void requestCloudSpeech(`客群透视完成，共${summary.value.length}个群组，主要标签包括${labels}。`);
    } else {
      void requestCloudSpeech("客群透视完成，但暂无可展示的分群结果。");
    }
  } catch (error: any) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const exportData = async () => {
  try {
    const resp = await http.post(`/export`, { target: "cluster", k: k.value }, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "customer_segments.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error: any) {
    console.error(error);
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

.control-bar { display: flex; gap: 24px; align-items: flex-end; }

.stepper-group .label {
  display: block;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 8px;
  font-weight: 600;
}

.stepper {
  display: flex;
  align-items: center;
  background: var(--bg-surface);
  border: 1px solid #E2E8F0;
  border-radius: var(--radius-sm);
  padding: 2px;
  box-shadow: var(--shadow-xs);
}

.step-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.step-btn:hover:not(:disabled) { background: #F1F5F9; color: var(--text-primary); }
.step-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.step-val {
  width: 40px;
  text-align: center;
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--brand-primary);
  font-size: 16px;
}

/* Layout */
.analysis-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
  align-items: start;
}

.card-panel {
  padding: 24px;
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.panel-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }

.chart-canvas { width: 100%; height: 400px; }

/* Table */
.table-scroll { overflow-x: auto; }
.bold { font-weight: 600; }

.cluster-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
  background: #FFFFFF;
  color: var(--badge-color);
  border: 1px solid var(--badge-color);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.tag-label {
  font-size: 12px;
  color: var(--text-secondary);
  background: #F1F5F9;
  padding: 4px 10px;
  border-radius: 6px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100px 0;
  color: var(--text-tertiary);
}
.empty-icon { margin-bottom: 16px; color: #CBD5E1; }
</style>
