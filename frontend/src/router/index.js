import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
    {
      path: '/', component: AppLayout,
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
        { path: 'purchases', name: 'purchases', component: () => import('@/views/PurchasesView.vue') },
        { path: 'sales', name: 'sales', component: () => import('@/views/SalesView.vue') },
        { path: 'reports', name: 'reports', component: () => import('@/views/ReportsView.vue') },
        { path: 'settings', name: 'settings', component: () => import('@/views/SettingsView.vue') },
      ]
    },
  ]
})

router.beforeEach((to) => {
  const token = localStorage.getItem('umoja_token')
  if (to.name !== 'login' && !token) return { name: 'login' }
  if (to.name === 'login' && token) return { name: 'dashboard' }
})

export default router
