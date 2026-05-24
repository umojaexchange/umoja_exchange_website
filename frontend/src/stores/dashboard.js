import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dashboardApi } from '@/api/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  const summary = ref(null)
  const charts = ref(null)
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [s, c] = await Promise.all([dashboardApi.summary(), dashboardApi.charts()])
      summary.value = s.data
      charts.value = c.data
    } finally { loading.value = false }
  }

  return { summary, charts, loading, fetchAll }
})
