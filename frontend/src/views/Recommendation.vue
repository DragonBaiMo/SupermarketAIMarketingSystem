<template>
  <div class="page-container">
    <!-- 顶部查询头 (Compact Header Search) -->
    <div class="search-header card-panel">
      <div class="header-title">
        <h2>精准营销</h2>
        <span class="subtitle">AI 协同过滤推荐</span>
      </div>
      
      <div class="search-row">
        <div class="search-input-group">
          <span class="search-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          </span>
          <input 
            v-model="customerId" 
            placeholder="输入客户 ID (Enter确认)" 
            @keyup.enter="fetchRecommend"
            class="main-search-input"
          />
        </div>
        
        <div class="setting-group">
          <span class="label">Top</span>
          <input type="number" v-model.number="topN" min="1" max="50" class="num-input" />
        </div>

        <button class="primary" @click="fetchRecommend" :disabled="loading">
          <span v-if="!loading">生成推荐</span>
          <span v-else class="spinner"></span>
        </button>
      </div>
    </div>

    <div class="results-container" v-if="items.length">
      <!-- 用户画像摘要栏 -->
      <div class="user-summary-bar">
        <div class="user-info">
          <div class="avatar">{{ customerId.slice(0, 1).toUpperCase() }}</div>
          <div class="info-text">
            <div class="u-id">Customer #{{ customerId }}</div>
            <div class="u-tag">推荐算法: Item-CF</div>
          </div>
        </div>
        <div class="actions">
           <button class="secondary small" @click="exportRecommend">
             <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
             导出方案
           </button>
        </div>
      </div>

      <!-- 推荐商品网格 -->
      <div class="product-grid">
        <div v-for="(item, idx) in items" :key="item.product_id" class="product-card">
          <div class="rank-badge">#{{ idx + 1 }}</div>
          
          <div class="card-content">
            <div class="p-header">
              <div class="p-name" :title="item.product_name">{{ item.product_name || '未知商品' }}</div>
              <div class="p-code">{{ item.product_id }}</div>
            </div>

            <div class="match-bar-row">
              <span class="label">匹配度</span>
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: Math.min((item.score || 0) * 10, 100) + '%' }"></div>
              </div>
              <span class="score-num">{{ item.score?.toFixed(2) }}</span>
            </div>
            
            <div class="reason-row">
              <span class="icon">💡</span>
              <span class="text">{{ item.reason }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-illustration">
        <div class="circle"></div>
        <div class="icon">🔍</div>
      </div>
      <p>请输入客户 ID 以获取 AI 推荐清单</p>
    </div>
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
const loading = ref(false);

const fetchRecommend = async () => {
  if (!customerId.value) return;
  loading.value = true;
  try {
    const resp = await http.post("/recommend", { customer_id: customerId.value, top_n: topN.value });
    items.value = resp.data.items || [];
  } catch (error: any) {
    console.error(error); 
  } finally {
    loading.value = false;
  }
};

const exportRecommend = async () => {
  if (!customerId.value) return;
  try {
    const resp = await http.post(`/export`, { target: "recommendation", customer_id: customerId.value, top_n: topN.value }, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `recommendation_${customerId.value}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error: any) {
    console.error(error);
  }
};
</script>

<style scoped>
/* Search Header (紧凑通栏) */
.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  margin-bottom: 24px;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.header-title h2 { font-size: 20px; font-weight: 700; margin: 0; color: var(--text-primary); }
.header-title .subtitle { font-size: 13px; color: var(--text-tertiary); }

.search-row { display: flex; gap: 16px; align-items: center; }

.search-input-group {
  position: relative;
  width: 300px;
}
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  display: flex;
}
.search-icon svg { width: 18px; height: 18px; }

.main-search-input {
  width: 100%;
  height: 40px;
  padding-left: 38px;
  padding-right: 12px;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}
.main-search-input:focus { border-color: var(--brand-primary); box-shadow: 0 0 0 3px var(--brand-shadow); }

.setting-group {
  display: flex;
  align-items: center;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 0 8px;
  height: 40px;
}
.setting-group .label { font-size: 12px; color: var(--text-secondary); margin-right: 4px; font-weight: 600; }
.num-input {
  width: 40px;
  border: none;
  background: transparent;
  text-align: center;
  font-weight: 600;
  height: 100%;
}

/* User Summary Bar */
.user-summary-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 8px;
}

.user-info { display: flex; align-items: center; gap: 12px; }
.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2563EB, #1D4ED8);
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
}
.u-id { font-size: 15px; font-weight: 700; color: var(--text-primary); }
.u-tag { font-size: 12px; color: var(--text-secondary); }

/* Product Grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.product-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  padding: 16px;
  position: relative;
  transition: all 0.2s;
  box-shadow: var(--shadow-xs);
}
.product-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: #93C5FD; }

.rank-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 12px;
  font-weight: 700;
  color: #CBD5E1;
  font-family: var(--font-mono);
}
.product-card:nth-child(1) .rank-badge { color: #F59E0B; } /* Gold for #1 */

.card-content { display: flex; flex-direction: column; gap: 12px; }
.p-header { padding-right: 24px; } /* Space for badge */
.p-name { font-size: 15px; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.p-code { font-size: 12px; color: var(--text-tertiary); font-family: var(--font-mono); }

.match-bar-row { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.label { color: var(--text-tertiary); }
.progress-track { flex: 1; height: 6px; background: #F1F5F9; border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: #2563EB; border-radius: 3px; }
.score-num { font-weight: 700; color: #2563EB; width: 30px; text-align: right; }

.reason-row {
  background: #F8FAFC;
  padding: 8px;
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  gap: 6px;
  line-height: 1.4;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 0;
  color: var(--text-tertiary);
}
.empty-illustration {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.circle {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 1px dashed #CBD5E1;
  border-radius: 50%;
  animation: spin 10s linear infinite;
}
.icon { font-size: 32px; position: relative; z-index: 1; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>