import { defineStore } from 'pinia'
import { ref } from 'vue'
import { settingsApi } from '@/api/settings'

export const useSettingsStore = defineStore('settings', () => {
  const data = ref(null)
  const loading = ref(false)

  async function fetch() {
    loading.value = true
    try { const { data: d } = await settingsApi.get(); data.value = d }
    finally { loading.value = false }
  }

  async function save(payload) {
    const { data: d } = await settingsApi.update(payload)
    data.value = d
    return d
  }

  return { data, loading, fetch, save }
})
