import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('umoja_user') || 'null'))
  const token = ref(localStorage.getItem('umoja_token') || '')
  const loading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isStaff = computed(() => ['admin','staff'].includes(user.value?.role))

  async function login({ username, password }) {
    loading.value = true; error.value = ''
    try {
      const { data } = await authApi.login({ username, password })
      token.value = data.access
      localStorage.setItem('umoja_token', data.access)
      if (data.refresh) localStorage.setItem('umoja_refresh', data.refresh)
      // Fetch user info
      const { data: me } = await authApi.me()
      user.value = me
      localStorage.setItem('umoja_user', JSON.stringify(me))
      router.push('/')
    } catch(e) {
      error.value = e.response?.data?.detail || 'Invalid credentials'
    } finally { loading.value = false }
  }

  async function logout() {
    try { await authApi.logout({ refresh: localStorage.getItem('umoja_refresh') }) } catch {}
    token.value = ''; user.value = null
    localStorage.removeItem('umoja_token'); localStorage.removeItem('umoja_refresh'); localStorage.removeItem('umoja_user')
    router.push('/login')
  }

  return { user, token, loading, error, isAuthenticated, isAdmin, isStaff, login, logout }
})
