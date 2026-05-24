import api from './index'
export const purchasesApi = {
  list: (params) => api.get('/purchases/', { params }),
  get: (id) => api.get(`/purchases/${id}/`),
  create: (data) => api.post('/purchases/', data),
  update: (id, data) => api.put(`/purchases/${id}/`, data),
  destroy: (id) => api.delete(`/purchases/${id}/`),
  inventory: () => api.get('/purchases/inventory/'),
}
