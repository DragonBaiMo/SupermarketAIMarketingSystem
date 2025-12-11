<template>
  <div class="dashboard-view">
    <!-- 页头 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">数据驾驶舱</h1>
        <p class="page-subtitle">实时监控系统核心指标与数据源状态</p>
      </div>
      <div class="header-right">
        <div class="date-badge">
          <span class="dot"></span>
          {{ currentDate }}
        </div>
      </div>
    </header>

    <!-- 控制台卡片 -->
    <section class="control-card">
      <div class="control-group">
        <label class="group-label">服务器数据源</label>
        <div class="input-row">
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            <input 
              v-model="loadPath" 
              type="text" 
              placeholder="输入服务器文件路径..." 
            />
          </div>
          <button class="primary" @click="loadByPath" :disabled="loading">
            <span v-if="!loading">同步数据</span>
            <span v-else>同步中...</span>
          </button>
        </div>
      </div>

      <div class="divider"></div>

      <div class="control-group">
        <label class="group-label">本地文件导入</label>
        <div class="upload-row">
          <input 
            type="file" 
            id="file-upload" 
            accept=".csv" 
            @change="handleFile" 
            class="hidden-input"
          />
          <label for="file-upload" class="file-dropzone" :class="{ 'has-file': file }">
            <div class="drop-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
            </div>
            <span class="drop-text">{{ file ? file.name : '点击上传 CSV 文件' }}</span>
          </label>
          <button 
            class="secondary" 
            @click="upload" 
            :disabled="!file || loading"
          >
            开始处理
          </button>
        </div>
      </div>

      <!-- 状态通知 -->
      <Transition name="fade">
        <div v-if="message" class="status-alert" :class="statusType">
          <span class="status-icon">
             <svg v-if="statusType==='success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
             <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          </span>
          {{ message }}
        </div>
      </Transition>
    </section>

    <!-- 核心指标网格 -->
    <main class="metrics-grid" v-if="overview">
      <div class="section-label">核心经营数据</div>
      
      <div class="cards-row">
        <StatCard title="总记录数" :value="formatNumber(overview.records)">
          <template #icon>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
          </template>
        </StatCard>
        
        <StatCard title="累计订单量" :value="formatNumber(overview.orders)" :trend="5.2">
          <template #icon>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
          </template>
        </StatCard>
        
        <StatCard title="活跃客户" :value="formatNumber(overview.customers)" :trend="-1.8">
          <template #icon>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          </template>
        </StatCard>
        
        <StatCard title="在售商品 SKU" :value="formatNumber(overview.products)">
          <template #icon>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
          </template>
        </StatCard>
      </div>

      <div class="section-label mt-lg">统计周期</div>
      <div class="cards-row split-row">
        <StatCard title="起始日期" :value="overview.start_date || '-'">
          <template #icon>
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
          </template>
        </StatCard>
        <StatCard title="截止日期" :value="overview.end_date || '-'">
           <template #icon>
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
           </template>
        </StatCard>
      </div>
    </main>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#E2E8F0" stroke-width="1"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
      </div>
      <div class="empty-text">
        <h3>系统待机中</h3>
        <p>请在上方控制台加载数据源以初始化系统。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
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
const loading = ref(false);
const message = ref("");
const statusType = ref<"success" | "error" | "info">("info");

const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
});

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('zh-CN').format(num);
};

const showMessage = (msg: string, type: "success" | "error" = "info") => {
  message.value = msg;
  statusType.value = type;
  setTimeout(() => message.value = "", 4000);
};

const fetchOverview = async () => {
  try {
    const resp = await http.get("/data/overview");
    overview.value = resp.data;
  } catch (error) {
    console.warn(error);
  }
};

const loadByPath = async () => {
  loading.value = true;
  try {
    const resp = await http.post("/data/load", { path: loadPath.value || undefined });
    overview.value = resp.data.overview;
    showMessage("数据源同步成功", "success");
  } catch (error: any) {
    showMessage(error.message || "同步失败", "error");
  } finally {
    loading.value = false;
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
  loading.value = true;
  const form = new FormData();
  form.append("file", file.value);
  try {
    const resp = await http.post("/data/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
    overview.value = resp.data.overview;
    showMessage("文件处理完成", "success");
    file.value = null; 
  } catch (error: any) {
    showMessage(error.message || "上传失败", "error");
  } finally {
    loading.value = false;
  }
};

onMounted(() => fetchOverview());
</script>

<style scoped>
.dashboard-view {
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 14px;
}

.date-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 100px;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  box-shadow: var(--shadow-xs);
}

.dot {
  width: 8px;
  height: 8px;
  background: #10B981;
  border-radius: 50%;
  box-shadow: 0 0 0 2px #D1FAE5;
}

/* Control Card */
.control-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 24px 32px;
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: flex-start;
  gap: 32px;
  border: 1px solid var(--border-light);
  margin-bottom: 40px;
  position: relative;
}

.control-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.group-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-row, .upload-row {
  display: flex;
  gap: 12px;
  height: 40px;
}

.divider {
  width: 1px;
  height: 60px;
  background: var(--border-light);
  margin-top: 10px;
}

.input-wrapper {
  flex: 1;
  position: relative;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 10px;
  width: 18px;
  height: 18px;
  color: var(--text-tertiary);
}

.input-wrapper input {
  padding-left: 36px;
}

.hidden-input { display: none; }

.file-dropzone {
  flex: 1;
  border: 1px dashed #CBD5E1;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: #F8FAFC;
}

.file-dropzone:hover {
  border-color: var(--brand-primary);
  background: #EFF6FF;
}

.file-dropzone.has-file {
  border-color: #059669;
  background: #ECFDF5;
  color: #059669;
}

.drop-icon {
  width: 20px;
  height: 20px;
  color: var(--text-tertiary);
}

.drop-text {
  font-size: 14px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Status Alert */
.status-alert {
  position: absolute;
  top: -16px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow-md);
  background: white;
}
.status-alert.success { color: #059669; border: 1px solid #A7F3D0; }
.status-alert.error { color: #DC2626; border: 1px solid #FECACA; }

.status-icon svg { width: 16px; height: 16px; }

/* Metrics */
.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-tertiary);
  margin-bottom: 16px;
  letter-spacing: 0.02em;
}
.mt-lg { margin-top: 40px; }

.cards-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}
.split-row {
  grid-template-columns: repeat(2, 1fr);
}

/* Empty State */
.empty-state {
  padding: 120px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--border-light);
  border-radius: var(--radius-lg);
  background: rgba(255,255,255,0.5);
}
.empty-text h3 { font-size: 18px; margin-bottom: 8px; color: var(--text-primary); }
.empty-text p { color: var(--text-secondary); }
</style>