import api from './index'
export const dashboardApi = {
  summary: () => api.get('/dashboard/summary/'),
  charts: () => api.get('/dashboard/charts/'),
}
