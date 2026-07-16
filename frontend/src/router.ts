import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'chat',
      component: () => import('./views/ChatView.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('./views/DashboardView.vue'),
    },
    {
      path: '/report',
      name: 'report',
      component: () => import('./views/ReportView.vue'),
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: () => import('./views/KnowledgeView.vue'),
    },
    {
      path: '/llmops',
      name: 'llmops',
      component: () => import('./views/LLMOpsView.vue'),
    },
  ],
})

export default router
