<template>
  <div class="section-card">
    <h2>客户聚类</h2>
    <div class="form-row">
      <label>聚类数 K</label>
      <input type="number" min="2" max="10" v-model.number="k" />
      <button class="primary" @click="run">计算聚类</button>
      <button class="secondary" @click="exportData">导出分群CSV</button>
    </div>
    <p style="color: #9ca3af">使用 RFM 指标 + KMeans 进行分群，给出业务解释。</p>
  </div>

  <div class="section-card" v-if="summary.length">
    <h3>分群概览</h3>
    <div ref="chartRef" class="chart-box"></div>
    <table class="table" style="margin-top: 12px">
      <thead>
        <tr>
          <th>群组</th>
          <th>人数</th>
          <th>R均值</th>
          <th>F均值</th>
          <th>M均值</th>
          <th>业务标签</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in summary" :key="item.cluster">
          <td>{{ item.cluster }}</td>
          <td>{{ item.count }}</td>
          <td>{{ item.R_mean?.toFixed(2) }}</td>
          <td>{{ item.F_mean?.toFixed(2) }}</td>
          <td>{{ item.M_mean?.toFixed(2) }}</td>
          <td>{{ item.label }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { nextTick, onBeforeUnmount, ref } from "vue";
import http from "../api/http";

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
let chart: echarts.ECharts | null = null;

const renderChart = () => {
  if (!chartRef.value || !summary.value.length) return;
  if (!chart) {
    chart = echarts.init(chartRef.value);
  }
  chart.setOption({
    tooltip: {},
    xAxis: { type: "category", data: summary.value.map((s) => `群组${s.cluster}`) },
    yAxis: { type: "value" },
    series: [
      {
        name: "人数",
        type: "bar",
        data: summary.value.map((s) => s.count)
      }
    ]
  });
};

const run = async () => {
  try {
    const resp = await http.post("/clustering", { k: k.value });
    summary.value = resp.data.summary || [];
    await nextTick();
    renderChart();
  } catch (error: any) {
    alert(error.message);
  }
};

const exportData = async () => {
  try {
    const resp = await http.post(`/export`, { target: "cluster", k: k.value }, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "clusters.csv");
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
