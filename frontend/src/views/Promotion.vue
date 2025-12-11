<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-content">
        <h2 class="title">促销策略筛选</h2>
        <p class="desc">基于 AI 模型的多维数据筛选，精准定位高潜力促销商品。</p>
      </div>
    </header>

    <!-- 稳态控制台 (Standard Filter Bar) -->
    <div class="filter-bar card-panel">
      <div class="filter-grid">
        <!-- 销量 -->
        <div class="filter-item">
          <label class="f-label">销量范围 (件)</label>
          <div class="range-group">
            <input type="number" v-model.number="rule.min_quantity" class="std-input" placeholder="Min" />
            <span class="sep">-</span>
            <input type="number" v-model.number="rule.max_quantity" class="std-input" placeholder="Max" />
          </div>
        </div>

        <!-- 利润 -->
        <div class="filter-item">
          <label class="f-label">最低利润率 (%)</label>
          <div class="input-wrapper">
            <input type="number" step="0.01" v-model.number="rule.min_profit_rate" class="std-input" />
          </div>
        </div>

        <!-- 折扣 -->
        <div class="filter-item">
          <label class="f-label">最大折扣 (%)</label>
          <div class="input-wrapper">
            <input type="number" step="0.01" v-model.number="rule.max_discount" class="std-input" />
          </div>
        </div>

        <!-- 操作区 -->
        <div class="filter-actions">
          <button class="secondary icon-only" @click="resetRules" title="重置条件">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path></svg>
          </button>
          <button class="primary" @click="run" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? '筛选中...' : '查询' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 结果列表 (Standard Grid) -->
    <div class="results-area" v-if="items.length">
      <div class="area-header">
        <h3 class="area-title">筛选结果 <span class="count-badge">{{ total }}</span></h3>
        <button class="secondary small" @click="exportData">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          导出
        </button>
      </div>

      <div class="cards-grid">
        <div v-for="item in items" :key="item.product_id" class="strategy-card">
          <div class="card-top">
            <div class="prod-id">#{{ item.product_id }}</div>
            <div class="prod-name" :title="item.product_name">{{ item.product_name || '未知商品' }}</div>
          </div>
          
          <div class="card-metrics">
            <div class="metric-col">
              <div class="label">销量</div>
              <div class="val">{{ item.quantity }}</div>
            </div>
            <div class="metric-col">
              <div class="label">利润率</div>
              <div class="val" :class="getProfitClass(item.profit_rate)">
                {{ (item.profit_rate * 100).toFixed(1) }}%
              </div>
            </div>
            <div class="metric-col">
              <div class="label">销售额</div>
              <div class="val">¥{{ formatMoney(item.sales) }}</div>
            </div>
          </div>

          <div class="card-reason">
            <div class="reason-title">策略依据</div>
            <p class="reason-text">{{ item.reason }}</p>
          </div>

          <div class="card-footer">
            <div class="discount-block">
              <span class="d-label">建议折扣</span>
              <span class="d-val">-{{ (item.discount * 100).toFixed(0) }}%</span>
            </div>
            <button class="secondary small">应用</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">🏷️</div>
      <p>请在上方设置条件并点击查询</p>
    </div>
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

const loading = ref(false);
const items = ref<PromotionItem[]>([]);
const total = ref(0);

const resetRules = () => {
  rule.value = {
    min_quantity: 50,
    max_quantity: 1000,
    min_profit_rate: 0.05,
    max_discount: 0.5
  };
};

const getProfitClass = (rate: number) => {
  if (rate > 0.2) return 'text-success';
  if (rate < 0.05) return 'text-error';
  return 'text-primary';
};

const formatMoney = (val: number) => new Intl.NumberFormat('zh-CN').format(Math.round(val));

const run = async () => {
  loading.value = true;
  try {
    const resp = await http.post("/promotion", rule.value);
    items.value = resp.data.items || [];
    total.value = resp.data.total || 0;
  } catch (error: any) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const exportData = async () => {
  try {
    const resp = await http.post(`/export`, { target: "promotion" }, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "promotion_candidates.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error: any) {
    console.error(error);
  }
};
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.title { font-size: 24px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.desc { color: var(--text-secondary); font-size: 14px; }

/* Filter Bar (稳固的条状容器) */
.filter-bar {
  padding: 20px 24px;
  margin-bottom: 32px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.filter-grid {
  display: flex;
  align-items: flex-end;
  gap: 24px;
  flex-wrap: wrap;
}

.filter-item { display: flex; flex-direction: column; gap: 8px; }
.f-label { font-size: 13px; font-weight: 600; color: var(--text-secondary); }

/* 标准输入框样式 */
.std-input {
  height: 36px;
  border: 1px solid #E2E8F0;
  border-radius: 6px;
  padding: 0 12px;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.2s;
  background: #fff;
  width: 100px;
}
.std-input:focus { border-color: var(--brand-primary); box-shadow: 0 0 0 3px var(--brand-shadow); }

.range-group { display: flex; align-items: center; gap: 8px; }
.sep { color: var(--text-tertiary); }

.filter-actions {
  margin-left: auto; /* 推到右侧 */
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Results */
.area-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.area-title { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.count-badge { background: #F1F5F9; padding: 2px 8px; border-radius: 10px; font-size: 12px; margin-left: 8px; color: var(--text-secondary); }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

/* Strategy Card (规整卡片) */
.strategy-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s;
}
.strategy-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: #BFDBFE; }

.card-top { padding-bottom: 12px; border-bottom: 1px solid var(--border-light); }
.prod-id { font-size: 12px; color: var(--text-tertiary); font-family: var(--font-mono); margin-bottom: 2px; }
.prod-name { font-size: 15px; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.card-metrics { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.metric-col .label { font-size: 11px; color: var(--text-tertiary); margin-bottom: 2px; }
.metric-col .val { font-size: 14px; font-weight: 600; color: var(--text-primary); font-family: var(--font-mono); }

.text-success { color: #059669; }
.text-error { color: #DC2626; }

.card-reason { background: #F8FAFC; padding: 10px; border-radius: 6px; flex: 1; }
.reason-title { font-size: 11px; font-weight: 600; color: var(--text-tertiary); margin-bottom: 4px; text-transform: uppercase; }
.reason-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }

.card-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 4px; }
.discount-block { display: flex; flex-direction: column; }
.d-label { font-size: 10px; color: var(--text-tertiary); }
.d-val { font-size: 18px; font-weight: 700; color: #DC2626; font-family: var(--font-mono); }

/* Empty State */
.empty-state { text-align: center; padding: 60px 0; color: var(--text-tertiary); }
.empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
</style>