<script setup lang="ts">
import logo from './assets/logo.svg';
</script>

<template>
  <div class="app-layout">
    <!-- 磨砂玻璃侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-box">
          <img :src="logo" alt="Logo" class="app-logo" />
        </div>
        <h1 class="app-name">智擎<span class="thin">系统</span></h1>
      </div>
      
      <nav class="nav-menu">
        <RouterLink to="/" class="nav-item" active-class="active">
          <span class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          </span>
          <span class="label">数据驾驶舱</span>
        </RouterLink>
        
        <RouterLink to="/clustering" class="nav-item" active-class="active">
          <span class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          </span>
          <span class="label">客群透视</span>
        </RouterLink>

        <RouterLink to="/forecast" class="nav-item" active-class="active">
          <span class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
          </span>
          <span class="label">趋势预测</span>
        </RouterLink>
        
        <RouterLink to="/promotion" class="nav-item" active-class="active">
          <span class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>
          </span>
          <span class="label">策略筛选</span>
        </RouterLink>
        
        <RouterLink to="/recommend" class="nav-item" active-class="active">
          <span class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"></path></svg>
          </span>
          <span class="label">精准营销</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <div class="user-card">
          <div class="avatar">A</div>
          <div class="info">
            <div class="name">Admin</div>
            <div class="role">超级管理员</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主视图区 -->
    <main class="main-container">
      <div class="content-wrapper">
        <RouterView v-slot="{ Component }">
          <Transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-app);
  /* 添加噪点纹理，增加高级感 */
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E");
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  position: fixed;
  height: 100vh;
  z-index: 100;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 12px 32px 12px;
}

.logo-box {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
  transition: transform 0.3s ease;
}

.logo-box:hover .app-logo {
  transform: scale(1.05);
}

.app-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}
.thin { font-weight: 400; color: var(--text-tertiary); margin-left: 4px; }

/* Navigation */
.nav-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s var(--ease-spring);
  font-weight: 500;
  position: relative;
}

.nav-item:hover {
  background: #F1F5F9;
  color: var(--text-primary);
}

.nav-item.active {
  background: #EFF6FF; /* 极淡的蓝色背景 */
  color: var(--brand-primary);
}

.icon-box {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-box svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s var(--ease-spring);
}

/* 选中时图标跳动 */
.nav-item.active .icon-box svg {
  transform: scale(1.1);
  stroke-width: 2.5;
}

/* Footer */
.sidebar-footer {
  padding-top: 20px;
  border-top: 1px solid var(--border-light);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 10px;
  transition: background 0.2s;
  cursor: pointer;
}
.user-card:hover { background: #F8FAFC; }

.avatar {
  width: 36px;
  height: 36px;
  background: #F1F5F9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text-secondary);
  border: 1px solid #E2E8F0;
}

.info { display: flex; flex-direction: column; }
.name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.role { font-size: 12px; color: var(--text-tertiary); }

/* Main Content */
.main-container {
  flex: 1;
  margin-left: 260px;
  padding: 40px 48px;
  max-width: 1600px; /* 限制最大宽，防止大屏太散 */
}

.content-wrapper {
  width: 100%;
}

/* Animations */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
