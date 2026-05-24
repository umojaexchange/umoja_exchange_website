import api from './index'
export const reportsApi = {
  exportPdf: (params) => api.get('/reports/export/pdf/', { params, responseType: 'blob' }),
  exportExcel: (params) => api.get('/reports/export/excel/', { params, responseType: 'blob' }),
}
