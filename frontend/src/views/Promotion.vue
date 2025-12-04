<template>
  <div class="section-card">
    <h2>促销候选筛选</h2>
    <div class="form-row">
      <label>最低销量</label>
      <input type="number" v-model.number="rule.min_quantity" />
      <label>最高销量</label>
      <input type="number" v-model.number="rule.max_quantity" />
    </div>
    <div class="form-row">
      <label>最低利润率</label>
      <input type="number" step="0.01" v-model.number="rule.min_profit_rate" />
      <label>最高折扣</label>
      <input type="number" step="0.01" v-model.number="rule.max_discount" />
    </div>
    <div class="form-row" style="gap: 8px">
      <button class="primary" @click="run">筛选</button>
      <button class="secondary" @click="exportData">导出CSV</button>
    </div>
  </div>

  <div class="section-card">
    <h3>候选商品（{{ total }} 个）</h3>
    <table class="table" v-if="items.length">
      <thead>
        <tr>
          <th>商品ID</th>
          <th>名称</th>
          <th>销量</th>
          <th>销售额</th>
          <th>利润率</th>
          <th>折扣</th>
          <th>理由</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.product_id">
          <td>{{ item.product_id }}</td>
          <td>{{ item.product_name }}</td>
          <td>{{ item.quantity }}</td>
          <td>{{ item.sales?.toFixed(2) }}</td>
          <td>{{ (item.profit_rate * 100).toFixed(2) }}%</td>
          <td>{{ item.discount?.toFixed(2) }}</td>
          <td>{{ item.reason }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else style="color: #9ca3af">暂无数据，请调整筛选条件。</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import http from "../api/http";

interface PromotionItem {
  product_id: string;
  product_name?: string;
  quantity: number;
  sales: number;
  profit_rate: number;
  discount: number;
  reason: string;
}

const rule = ref({
  min_quantity: 50,
  max_quantity: 1000,
  min_profit_rate: 0.05,
  max_discount: 0.5
});

const items = ref<PromotionItem[]>([]);
const total = ref(0);

const run = async () => {
  try {
    const resp = await http.post("/promotion", rule.value);
    items.value = resp.data.items || [];
    total.value = resp.data.total || 0;
  } catch (error: any) {
    alert(error.message);
  }
};

const exportData = async () => {
  try {
    const resp = await http.post(`/export`, { target: "promotion" }, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "promotion.csv");
    document.body.appendChild(link);
    link.click();
  } catch (error: any) {
    alert(error.message);
  }
};
</script>
