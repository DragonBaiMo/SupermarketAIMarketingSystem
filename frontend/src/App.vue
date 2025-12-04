<template>
  <div class="app-shell">
    <aside class="sidebar">
      <h1>超市AI营销系统</h1>
      <nav>
        <RouterLink to="/">数据与总览</RouterLink>
        <RouterLink to="/recommend">客户推荐</RouterLink>
        <RouterLink to="/promotion">促销分析</RouterLink>
        <RouterLink to="/forecast">销售预测</RouterLink>
        <RouterLink to="/clustering">客户分群</RouterLink>
      </nav>
    </aside>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts"></script>
