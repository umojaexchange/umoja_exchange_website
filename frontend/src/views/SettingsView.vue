<template>
  <div class="animate-up" style="max-width:720px">
    <div class="page-header">
      <div class="page-header-left"><h1>{{ t('settings') }}</h1><p>Configure system parameters and notifications</p></div>
      <button v-if="authStore.isAdmin" class="btn btn-primary" :disabled="saving" @click="handleSave">
        <span v-if="saving" class="spinner spinner-sm" />{{ t('saveSettings') }}
      </button>
    </div>

    <div v-if="store.loading" style="padding:60px;text-align:center"><div class="spinner" /></div>

    <template v-else-if="store.data">
      <!-- Rate Limits -->
      <div class="data-table-wrapper" style="margin-bottom:16px">
        <div style="padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px">
          <div style="width:4px;height:24px;background:#FACC15;border-radius:2px"/><span style="font-size:15px;font-weight:700;color:var(--text)">{{ t('rateLimits') }}</span>
        </div>
        <div style="padding:20px"><div class="form-row">
          <div class="form-group"><label class="field-label">{{ t('minRate') }}</label><input v-model="form.min_rate" type="number" step="0.01" class="field-input" :disabled="!authStore.isAdmin" /></div>
          <div class="form-group"><label class="field-label">{{ t('maxRate') }}</label><input v-model="form.max_rate" type="number" step="0.01" class="field-input" :disabled="!authStore.isAdmin" /></div>
        </div></div>
      </div>

      <!-- Asset Limits -->
      <div class="data-table-wrapper" style="margin-bottom:16px">
        <div style="padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px">
          <div style="width:4px;height:24px;background:#3B82F6;border-radius:2px"/><span style="font-size:15px;font-weight:700;color:var(--text)">{{ t('assetLimits') }}</span>
        </div>
        <div style="padding:20px"><div class="form-row">
          <div class="form-group"><label class="field-label">{{ t('minAsset') }}</label><input v-model="form.min_asset_value" type="number" step="0.01" class="field-input" :disabled="!authStore.isAdmin" /></div>
          <div class="form-group"><label class="field-label">{{ t('maxAsset') }}</label><input v-model="form.max_asset_value" type="number" step="0.01" class="field-input" :disabled="!authStore.isAdmin" /></div>
        </div></div>
      </div>

      <!-- Capital -->
      <div class="data-table-wrapper" style="margin-bottom:16px">
        <div style="padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px">
          <div style="width:4px;height:24px;background:#10B981;border-radius:2px"/><span style="font-size:15px;font-weight:700;color:var(--text)">{{ t('capitalMonitoring') }}</span>
        </div>
        <div style="padding:20px">
          <div class="form-row" style="margin-bottom:16px">
            <div class="form-group"><label class="field-label">{{ t('companyCapital') }}</label><input v-model="form.company_capital" type="number" step="0.01" class="field-input" :disabled="!authStore.isAdmin" /></div>
            <div class="form-group"><label class="field-label">{{ t('minThreshold') }}</label><input v-model="form.min_threshold" type="number" step="0.01" class="field-input" :disabled="!authStore.isAdmin" /></div>
          </div>
          <!-- Capital bar -->
          <div v-if="form.company_capital && form.min_threshold" style="padding:12px;background:var(--bg-input);border-radius:10px;border:1px solid var(--border)">
            <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted);margin-bottom:8px;font-weight:600">
              <span>Threshold: {{ fmtN(form.min_threshold) }}</span><span>Capital: {{ fmtN(form.company_capital) }}</span>
            </div>
            <div style="width:100%;height:8px;background:var(--border);border-radius:20px;overflow:hidden">
              <div :style="{width:Math.min(100,capPct)+'%',height:'100%',borderRadius:'20px',background:capPct>50?'#10B981':capPct>20?'#FACC15':'#EF4444',transition:'all .5s'}" />
            </div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:6px">{{ capPct.toFixed(0) }}% above threshold</div>
          </div>
        </div>
      </div>

      <!-- Email -->
      <div class="data-table-wrapper" style="margin-bottom:16px">
        <div style="padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px">
          <div style="width:4px;height:24px;background:#8B5CF6;border-radius:2px"/><span style="font-size:15px;font-weight:700;color:var(--text)">{{ t('notifications') }}</span>
        </div>
        <div style="padding:20px">
          <div class="form-group">
            <label class="field-label">{{ t('reportEmail') }}</label>
            <input v-model="form.report_email" type="email" class="field-input" :disabled="!authStore.isAdmin" placeholder="admin@example.com" />
            <div style="font-size:11px;color:var(--text-muted);margin-top:6px">Daily and monthly reports will be sent here</div>
          </div>
        </div>
      </div>

      <div style="text-align:right;font-size:12px;color:var(--text-light)">{{ t('lastUpdated') }}: {{ fmtDate(store.data.updated_at) }}</div>
    </template>
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'
import { useToast } from '@/composables/useToast'

const store = useSettingsStore(); const authStore = useAuthStore()
const { t } = useI18n(); const toast = useToast()
const saving = ref(false)
const form = reactive({ min_rate:0, max_rate:0, min_asset_value:0, max_asset_value:0, company_capital:0, min_threshold:0, report_email:'' })

const fmtN = (v) => v!=null ? Number(v).toLocaleString('en-TZ',{minimumFractionDigits:0,maximumFractionDigits:0}) : '—'
const fmtDate = (d) => d ? new Date(d).toLocaleDateString('en-TZ',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'}) : '—'
const capPct = computed(() => { const c=Number(form.company_capital),th=Number(form.min_threshold); if(!th) return 100; return Math.max(0,((c-th)/th)*100) })

watch(() => store.data, (d) => { if (d) Object.assign(form, { ...d }) }, { immediate: true })

async function handleSave() {
  saving.value = true
  try { await store.save({ ...form }); toast.success('Settings saved') }
  catch(e) { toast.error(e.response?.data?.detail || 'Failed to save') }
  finally { saving.value=false }
}

onMounted(() => store.fetch())
</script>
