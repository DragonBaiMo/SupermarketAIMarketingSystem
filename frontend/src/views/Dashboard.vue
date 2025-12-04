<template>
  <div class="section-card">
    <h2>数据管理</h2>
    <div class="form-row">
      <label>指定 CSV 路径</label>
      <input v-model="loadPath" style="flex: 1" placeholder="例如 data/sales_data.csv" />
      <button class="primary" @click="loadByPath">读取</button>
    </div>
    <div class="form-row">
      <label>上传 CSV 文件</label>
      <input type="file" accept=".csv" @change="handleFile" />
      <button class="secondary" @click="upload" :disabled="!file">上传并加载</button>
    </div>
    <p style="color: #6b7280">若未指定路径，后台会尝试读取 data 目录下的 sales_data.csv。</p>
  </div>

  <div class="section-card">
    <h2>数据概览</h2>
    <div class="stat-grid" v-if="overview">
      <StatCard title="记录数" :value="overview.records" />
      <StatCard title="订单数" :value="overview.orders" />
      <StatCard title="客户数" :value="overview.customers" />
      <StatCard title="商品数" :value="overview.products" />
      <StatCard title="起始日期" :value="overview.start_date || '-'" />
      <StatCard title="结束日期" :value="overview.end_date || '-'" />
    </div>
    <p v-else style="color: #9ca3af">尚未加载数据，请先上传或读取 CSV。</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import http from "../api/http";
import StatCard from "../components/StatCard.vue";

type Overview = {
  records: number;
  orders: number;
  customers: number;
  products: number;
  start_date?: string | null;
  end_date?: string | null;
};

const overview = ref<Overview | null>(null);
const loadPath = ref("");
const file = ref<File | null>(null);

const fetchOverview = async () => {
  try {
    const resp = await http.get("/data/overview");
    overview.value = resp.data;
  } catch (error) {
    console.warn(error);
  }
};

const loadByPath = async () => {
  try {
    const resp = await http.post("/data/load", { path: loadPath.value || undefined });
    overview.value = resp.data.overview;
    alert("加载成功");
  } catch (error: any) {
    alert(error.message);
  }
};

const handleFile = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    file.value = target.files[0];
  }
};

const upload = async () => {
  if (!file.value) return;
  const form = new FormData();
  form.append("file", file.value);
  try {
    const resp = await http.post("/data/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
    overview.value = resp.data.overview;
    alert("上传并加载成功");
  } catch (error: any) {
    alert(error.message);
  }
};

onMounted(() => fetchOverview());
</script>
