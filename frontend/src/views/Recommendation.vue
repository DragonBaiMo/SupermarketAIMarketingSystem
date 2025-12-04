<template>
  <div class="section-card">
    <h2>客户个性化推荐</h2>
    <div class="form-row">
      <label>客户ID</label>
      <input v-model="customerId" placeholder="输入客户编号" style="flex: 1" />
    </div>
    <div class="form-row">
      <label>推荐数量</label>
      <input type="number" v-model.number="topN" min="1" max="20" style="width: 120px" />
    </div>
    <div class="form-row" style="gap: 8px">
      <button class="primary" @click="fetchRecommend">生成推荐</button>
      <button class="secondary" @click="exportRecommend">导出CSV</button>
    </div>
    <p style="color: #9ca3af">提示：首次使用前请先在数据管理中加载销售数据。</p>
  </div>

  <div class="section-card">
    <h3>推荐结果</h3>
    <table class="table" v-if="items.length">
      <thead>
        <tr>
          <th>商品ID</th>
          <th>商品名称</th>
          <th>推荐理由</th>
          <th>得分</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.product_id">
          <td>{{ item.product_id }}</td>
          <td>{{ item.product_name }}</td>
          <td>{{ item.reason }}</td>
          <td>{{ item.score?.toFixed(2) }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else style="color: #9ca3af">暂无数据，请输入客户后生成。</p>
  </div>
</template>

<script setup lang="ts">
import http from "../api/http";
import { ref } from "vue";

interface RecommendItem {
  product_id: string;
  product_name?: string;
  reason: string;
  score?: number;
}

const customerId = ref("");
const topN = ref(5);
const items = ref<RecommendItem[]>([]);

const fetchRecommend = async () => {
  if (!customerId.value) {
    alert("请输入客户ID");
    return;
  }
  try {
    const resp = await http.post("/recommend", { customer_id: customerId.value, top_n: topN.value });
    items.value = resp.data.items || [];
  } catch (error: any) {
    alert(error.message);
  }
};

const exportRecommend = async () => {
  if (!customerId.value) {
    alert("请输入客户ID");
    return;
  }
  try {
    const resp = await http.post(`/export`, { target: "recommendation", customer_id: customerId.value, top_n: topN.value }, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "recommendation.csv");
    document.body.appendChild(link);
    link.click();
  } catch (error: any) {
    alert(error.message);
  }
};
</script>
