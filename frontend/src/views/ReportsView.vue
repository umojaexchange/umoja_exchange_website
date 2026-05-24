<template>
  <div class="animate-up">
    <div class="page-header">
      <div class="page-header-left"><h1>{{ t('reports') }}</h1><p>Generate and download financial reports</p></div>
    </div>
    <!-- Type tabs -->
    <div style="display:flex;gap:8px;margin-bottom:20px">
      <button v-for="tp in types" :key="tp.v" @click="activeType=tp.v"
        :class="['btn', activeType===tp.v ? 'btn-primary' : 'btn-secondary']">
        {{ t(tp.key) }}
      </button>
    </div>
    <!-- Filters -->
    <div class="data-table-wrapper" style="margin-bottom:20px">
      <div class="filters-bar">
        <span style="font-size:13px;font-weight:700;color:var(--text)">{{ t('filter') }}</span>
        <div class="form-group" style="flex-direction:row;align-items:center;gap:8px">
          <label class="field-label" style="margin:0;white-space:nowrap">{{ t('dateFrom') }}</label>
          <input v-model="filters.date_from" type="date" class="filter-input" />
        </div>
        <div class="form-group" style="flex-direction:row;align-items:center;gap:8px">
          <label class="field-label" style="margin:0;white-space:nowrap">{{ t('dateTo') }}</label>
          <input v-model="filters.date_to" type="date" class="filter-input" />
        </div>
        <button class="btn btn-secondary btn-sm" @click="Object.assign(filters,{date_from:'',date_to:''})">{{ t('clearFilters') }}</button>
      </div>
    </div>
    <!-- Export cards -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
      <div class="stat-card" style="padding:28px;--accent-color:#EF4444">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px">
          <div style="width:56px;height:56px;border-radius:16px;background:#FEE2E2;display:flex;align-items:center;justify-content:center;font-size:28px">📄</div>
          <div>
            <div style="font-size:17px;font-weight:800;color:var(--text)">PDF {{ t('reports') }}</div>
            <div style="font-size:13px;color:var(--text-muted)">{{ activeLabel }} — formatted for print</div>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:20px">
          <div style="font-size:12px;color:var(--text-muted);display:flex;align-items:center;gap:6px">✓ Branded header</div>
          <div style="font-size:12px;color:var(--text-muted);display:flex;align-items:center;gap:6px">✓ Full table with totals</div>
          <div style="font-size:12px;color:var(--text-muted);display:flex;align-items:center;gap:6px">✓ Date range filtering</div>
        </div>
        <button @click="exportFile('pdf')" :disabled="pdfLoading" class="btn btn-primary" style="width:100%;justify-content:center">
          <span v-if="pdfLoading" class="spinner spinner-sm" />
          <svg v-else style="width:16px;height:16px" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          {{ pdfLoading ? t('generating') : t('exportPDF') }}
        </button>
      </div>

      <div class="stat-card" style="padding:28px;--accent-color:#10B981">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px">
          <div style="width:56px;height:56px;border-radius:16px;background:#D1FAE5;display:flex;align-items:center;justify-content:center;font-size:28px">📊</div>
          <div>
            <div style="font-size:17px;font-weight:800;color:var(--text)">Excel {{ t('reports') }}</div>
            <div style="font-size:13px;color:var(--text-muted)">{{ activeLabel }} — ready for analysis</div>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:20px">
          <div style="font-size:12px;color:var(--text-muted)">✓ Styled with brand colors</div>
          <div style="font-size:12px;color:var(--text-muted)">✓ Zebra-striped rows</div>
          <div style="font-size:12px;color:var(--text-muted)">✓ Auto-computed totals row</div>
        </div>
        <button @click="exportFile('excel')" :disabled="excelLoading" class="btn btn-primary" style="width:100%;justify-content:center">
          <span v-if="excelLoading" class="spinner spinner-sm" />
          <svg v-else style="width:16px;height:16px" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          {{ excelLoading ? t('generating') : t('exportExcel') }}
        </button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, computed } from 'vue'
import { reportsApi } from '@/api/reports'
import { useI18n } from '@/composables/useI18n'
import { useToast } from '@/composables/useToast'

const { t } = useI18n(); const toast = useToast()
const activeType = ref('purchases')
const pdfLoading = ref(false); const excelLoading = ref(false)
const filters = reactive({ date_from:'', date_to:'' })
const types = [{ v:'purchases', key:'purchases' },{ v:'sales', key:'sales' }]
const activeLabel = computed(() => types.find(tp=>tp.v===activeType.value)?.v.charAt(0).toUpperCase()+types.find(tp=>tp.v===activeType.value)?.v.slice(1))

function dl(blob, name) { const u=URL.createObjectURL(blob), a=document.createElement('a'); a.href=u; a.download=name; document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(u) }

async function exportFile(fmt) {
  const loading = fmt==='pdf' ? pdfLoading : excelLoading; loading.value=true
  try {
    const params = { type: activeType.value }
    if (filters.date_from) params.date_from = filters.date_from
    if (filters.date_to) params.date_to = filters.date_to
    const { data } = fmt==='pdf' ? await reportsApi.exportPdf(params) : await reportsApi.exportExcel(params)
    const ext = fmt==='pdf'?'pdf':'xlsx'
    const mime = fmt==='pdf'?'application/pdf':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    dl(new Blob([data],{type:mime}), `umoja_${activeType.value}_report.${ext}`)
    toast.success(`${activeLabel.value} ${fmt.toUpperCase()} downloaded`)
  } catch { toast.error('Failed to generate report') } finally { loading.value=false }
}
</script>
