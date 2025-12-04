<template>
  <div class="section-card">
    <h2>销售额与利润预测</h2>
    <div class="form-row">
      <label>预测月份数</label>
      <input type="number" min="1" max="12" v-model.number="months" />
      <button class="primary" @click="run">开始预测</button>
      <button class="secondary" @click="exportData">导出预测CSV</button>
    </div>
    <p style="color: #9ca3af">默认按月聚合，使用线性回归生成趋势预测。</p>
  </div>

  <div class="section-card" v-if="chartData.length">
    <h3>趋势图</h3>
    <div ref="chartRef" class="chart-box"></div>
  </div>
  <div class="section-card" v-if="summary">
    <h3>预测摘要</h3>
    <p>{{ summary }}</p>
  </div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { nextTick, onBeforeUnmount, ref } from "vue";
import http from "../api/http";

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
let chart: echarts.ECharts | null = null;

const renderChart = () => {
  if (!chartRef.value) return;
  if (!chart) {
    chart = echarts.init(chartRef.value);
  }
  const historyPeriods = chartData.value.map((item) => item.period);
  const forecastPeriods = forecastData.value.map((item) => item.period);
  chart.setOption({
    tooltip: { trigger: "axis" },
    legend: { data: ["历史销售", "历史利润", "预测销售", "预测利润"] },
    xAxis: { type: "category", data: [...historyPeriods, ...forecastPeriods] },
    yAxis: { type: "value" },
    series: [
      {
        name: "历史销售",
        type: "line",
        data: chartData.value.map((i) => i.sales)
      },
      {
        name: "历史利润",
        type: "line",
        data: chartData.value.map((i) => i.profit)
      },
      {
        name: "预测销售",
        type: "line",
        data: new Array(chartData.value.length).fill(null).concat(forecastData.value.map((i) => i.sales)),
        lineStyle: { type: "dashed" }
      },
      {
        name: "预测利润",
        type: "line",
        data: new Array(chartData.value.length).fill(null).concat(forecastData.value.map((i) => i.profit)),
        lineStyle: { type: "dashed" }
      }
    ]
  });
};

const run = async () => {
  try {
    const resp = await http.post("/forecast", { months: months.value });
    chartData.value = resp.data.history || [];
    forecastData.value = resp.data.forecast || [];
    summary.value = resp.data.summary || "";
    await nextTick();
    renderChart();
  } catch (error: any) {
    alert(error.message);
  }
};

const exportData = async () => {
  try {
    const resp = await http.post(`/export`, { target: "forecast", months: months.value }, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "forecast.csv");
    document.body.appendChild(link);
    link.click();
  } catch (error: any) {
    alert(error.message);
  }
};

onBeforeUnmount(() => {
  chart?.dispose();
  chart = null;
});
</script>
