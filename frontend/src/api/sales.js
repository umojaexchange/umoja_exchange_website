import api from './index'
export const salesApi = {
  list: (params) => api.get('/sales/', { params }),
  get: (id) => api.get(`/sales/${id}/`),
  create: (data) => api.post('/sales/create/', data),
  destroy: (id) => api.delete(`/sales/${id}/`),
}
