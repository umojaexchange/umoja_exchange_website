import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('umoja_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status === 401 && !err.config._retry) {
      err.config._retry = true
      try {
        const refresh = localStorage.getItem('umoja_refresh')
        if (!refresh) throw new Error('no refresh')
        const { data } = await axios.post('/api/v1/auth/refresh/', { refresh })
        localStorage.setItem('umoja_token', data.access)
        err.config.headers.Authorization = `Bearer ${data.access}`
        return api(err.config)
      } catch {
        localStorage.removeItem('umoja_token'); localStorage.removeItem('umoja_refresh'); localStorage.removeItem('umoja_user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api
