import api from './index'
export const authApi = {
  login: (data) => api.post('/auth/login/', data),
  refresh: (data) => api.post('/auth/refresh/', data),
  logout: (data) => api.post('/auth/logout/', data),
  me: () => api.get('/auth/me/'),
}
