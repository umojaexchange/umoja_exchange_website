import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { purchasesApi } from '@/api/purchases'

export const usePurchasesStore = defineStore('purchases', () => {
  const items = ref([])
  const total = ref(0)
  const loading = ref(false)
  const inventory = reactive({ total_available_usdt: 0, active_lots: 0 })

  async function fetchAll(params = {}) {
    loading.value = true
    try {
      const { data } = await purchasesApi.list(params)
      items.value = data.results ?? data
      total.value = data.count ?? data.length
    } finally { loading.value = false }
  }

  async function fetchInventory() {
    try {
      const { data } = await purchasesApi.inventory()
      Object.assign(inventory, data)
    } catch { /* inventory is optional */ }
  }

  async function create(payload) {
    const { data } = await purchasesApi.create(payload)
    await fetchAll()
    return data
  }

  async function update(id, payload) {
    const { data } = await purchasesApi.update(id, payload)
    await fetchAll()
    return data
  }

  async function remove(id) {
    await purchasesApi.destroy(id)
    await fetchAll()
  }

  return { items, total, loading, inventory, fetchAll, fetchInventory, create, update, remove }
})
