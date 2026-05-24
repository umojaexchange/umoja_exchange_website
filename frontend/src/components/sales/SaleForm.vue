<template>
  <form @submit.prevent="handleSubmit" class="animate-fade" novalidate>
    <div class="form-row">
      <div class="form-group">
        <label class="field-label">{{ t('usdtAmount') }} *</label>
        <input v-model="form.usdt_amount" type="number" step="0.01" min="0.01"
               class="field-input" placeholder="e.g. 500" required />
      </div>
      <div class="form-group">
        <label class="field-label">{{ t('saleRate') }} *</label>
        <input v-model="form.sale_rate_tzs" type="number" step="0.01" min="0.01"
               class="field-input" placeholder="e.g. 2700" required />
      </div>
    </div>

    <!-- Preview -->
    <div v-if="form.usdt_amount && form.sale_rate_tzs" class="calc-preview">
      <div class="calc-preview-label">Customer Pays</div>
      <div class="calc-preview-value">TZS {{ calcPaid }}</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.3);margin-top:4px">FIFO profit computed on save</div>
    </div>

    <div class="form-group" style="margin-top:4px">
      <label class="field-label">{{ t('paymentMethod') }} *</label>
      <select v-model="form.payment_method" class="field-input" required>
        <option value="" disabled>Select method...</option>
        <optgroup label="Banks">
          <option v-for="m in bankMethods" :key="m.v" :value="m.v">{{ m.l }}</option>
        </optgroup>
        <optgroup label="Mobile Money">
          <option v-for="m in mobileMethods" :key="m.v" :value="m.v">{{ m.l }}</option>
        </optgroup>
        <option value="cash">Cash</option>
      </select>
    </div>

    <div class="form-group">
      <label class="field-label">{{ t('customerName') }} *</label>
      <input v-model="form.customer_name" type="text" class="field-input"
             :placeholder="t('customerName')" required />
    </div>

    <div class="form-group">
      <label class="field-label">{{ t('notes') }}</label>
      <textarea v-model="form.notes" rows="2" class="field-input" style="resize:none" :placeholder="t('notes')+'...'" />
    </div>

    <div style="padding:10px 14px;background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:10px;margin-top:4px">
      <p style="font-size:12px;color:#D97706;margin:0">⚡ FIFO engine will consume oldest inventory lots first and compute weighted average profit automatically.</p>
    </div>
  </form>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { useI18n } from '@/composables/useI18n'

defineProps({ loading: Boolean })
const emit = defineEmits(['submit'])
const { t } = useI18n()

const bankMethods = [
  { v:'crdb',l:'CRDB Bank' },{ v:'nmb',l:'NMB Bank' },{ v:'nbc',l:'NBC Bank' },
  { v:'equity',l:'Equity Bank' },{ v:'absa',l:'Absa Bank' },{ v:'stanbic',l:'Stanbic Bank' },
  { v:'exim',l:'Exim Bank' },{ v:'boa',l:'BOA Bank' },
]
const mobileMethods = [
  { v:'mpesa',l:'M-Pesa' },{ v:'airtel',l:'Airtel Money' },
  { v:'tigo',l:'Tigo Pesa' },{ v:'halopesa',l:'HaloPesa' },
]

const form = reactive({ usdt_amount:'', sale_rate_tzs:'', payment_method:'', customer_name:'', notes:'' })

const calcPaid = computed(() => {
  const a = parseFloat(form.usdt_amount||0), r = parseFloat(form.sale_rate_tzs||0)
  return (a*r).toLocaleString('en-TZ',{minimumFractionDigits:2,maximumFractionDigits:2})
})

function handleSubmit() {
  if (!form.usdt_amount || !form.sale_rate_tzs || !form.payment_method || !form.customer_name) return
  emit('submit', { ...form })
}

defineExpose({ submit: handleSubmit })
</script>
