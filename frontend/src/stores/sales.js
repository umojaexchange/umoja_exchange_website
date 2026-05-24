import { defineStore } from 'pinia'
import { ref } from 'vue'
import { salesApi } from '@/api/sales'

export const useSalesStore = defineStore('sales', () => {
  const items = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchAll(params = {}) {
    loading.value = true
    try {
      const { data } = await salesApi.list(params)
      items.value = data.results ?? data
      total.value = data.count ?? data.length
    } finally { loading.value = false }
  }

  async function create(payload) {
    const { data } = await salesApi.create(payload)
    await fetchAll()
    return data
  }

  async function remove(id) {
    await salesApi.destroy(id)
    await fetchAll()
  }

  return { items, total, loading, fetchAll, create, remove }
})
