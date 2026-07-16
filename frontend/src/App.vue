<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1 class="logo">FinAgent</h1>
        <p class="subtitle">LLM + Agent + RAG 智能投研平台</p>
      </div>

      <nav class="nav-menu">
        <router-link to="/" class="nav-item" active-class="active">
          <span class="nav-icon nav-icon-chat"></span>
          <span>智能对话</span>
        </router-link>
        <router-link to="/dashboard" class="nav-item" active-class="active">
          <span class="nav-icon nav-icon-dashboard"></span>
          <span>数据看板</span>
        </router-link>
        <router-link to="/report" class="nav-item" active-class="active">
          <span class="nav-icon nav-icon-report"></span>
          <span>报告中心</span>
        </router-link>
        <router-link to="/knowledge" class="nav-item" active-class="active">
          <span class="nav-icon nav-icon-knowledge"></span>
          <span>知识库</span>
        </router-link>
        <router-link to="/llmops" class="nav-item" active-class="active">
          <span class="nav-icon nav-icon-monitor"></span>
          <span>LLMOps</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="status-indicator">
          <span class="status-dot"></span>
          <span>系统运行中</span>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background: #0a0e1a;
  color: #e0e6ed;
}

/* ===== 侧边栏 ===== */
.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #0f1629 0%, #1a1f35 100%);
  border-right: 1px solid rgba(99, 179, 237, 0.15);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(99, 179, 237, 0.1);
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: #63b3ed;
  margin: 0;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 11px;
  color: #718096;
  margin: 6px 0 0;
  line-height: 1.4;
}

/* ===== 导航菜单 ===== */
.nav-menu {
  flex: 1;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  color: #a0aec0;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(99, 179, 237, 0.1);
  color: #63b3ed;
}

.nav-item.active {
  background: rgba(99, 179, 237, 0.15);
  color: #63b3ed;
  border-left-color: #63b3ed;
}

/* ===== CSS 图标（替代 emoji） ===== */
.nav-icon {
  display: inline-block;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  flex-shrink: 0;
}

.nav-icon-chat {
  background: linear-gradient(135deg, #63b3ed, #4299e1);
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z'/%3E%3C/svg%3E") center/contain no-repeat;
}

.nav-icon-dashboard {
  background: #68d391;
  clip-path: polygon(0% 0%, 48% 0%, 48% 48%, 0% 48%, 0% 100%, 48% 100%, 48% 52%, 100% 52%, 100% 100%, 52% 100%, 52% 48%, 100% 48%, 100% 0%, 52% 0%, 52% 0%);
}

.nav-icon-report {
  background: #f6ad55;
  border-radius: 2px;
}

.nav-icon-knowledge {
  background: #b794f4;
  border-radius: 2px;
}

.nav-icon-monitor {
  background: #fc8181;
  border-radius: 50%;
}

/* ===== 侧边栏底部 ===== */
.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(99, 179, 237, 0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #68d391;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #68d391;
  box-shadow: 0 0 8px rgba(104, 211, 145, 0.5);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ===== 主内容区 ===== */
.main-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
