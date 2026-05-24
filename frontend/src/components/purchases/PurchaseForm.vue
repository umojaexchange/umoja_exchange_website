<template>
  <form @submit.prevent="handleSubmit" class="animate-fade" novalidate>
    <div class="form-row">
      <div class="form-group">
        <label class="field-label">{{ t('usdtAmount') }} *</label>
        <input v-model="form.usdt_amount" type="number" step="0.01" min="0.01"
               class="field-input" :placeholder="'e.g. 1000'" required />
      </div>
      <div class="form-group">
        <label class="field-label">{{ t('rateTZS') }} *</label>
        <input v-model="form.rate_tzs" type="number" step="0.01" min="0.01"
               class="field-input" :placeholder="'e.g. 2650'" required />
      </div>
    </div>

    <!-- Live preview -->
    <div v-if="form.usdt_amount && form.rate_tzs" class="calc-preview">
      <div class="calc-preview-label">{{ t('amountPaid') }}</div>
      <div class="calc-preview-value">TZS {{ calcAmount }}</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.3);margin-top:4px">{{ form.usdt_amount }} × {{ form.rate_tzs }}</div>
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
      <label class="field-label">{{ t('supplierName') }} *</label>
      <input v-model="form.supplier_name" type="text" class="field-input"
             :placeholder="t('supplierName')" required />
    </div>

    <div class="form-group">
      <label class="field-label">{{ t('notes') }}</label>
      <textarea v-model="form.notes" rows="2" class="field-input" style="resize:none"
                :placeholder="t('notes')+'...'" />
    </div>
  </form>
</template>

<script setup>
import { reactive, computed, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'

const props = defineProps({ initial: Object, loading: Boolean })
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

const form = reactive({ usdt_amount:'', rate_tzs:'', payment_method:'', supplier_name:'', notes:'' })

watch(() => props.initial, (val) => {
  if (val) Object.assign(form, { usdt_amount: val.usdt_amount, rate_tzs: val.rate_tzs, payment_method: val.payment_method, supplier_name: val.supplier_name, notes: val.notes||'' })
  else Object.assign(form, { usdt_amount:'', rate_tzs:'', payment_method:'', supplier_name:'', notes:'' })
}, { immediate: true })

const calcAmount = computed(() => {
  const a = parseFloat(form.usdt_amount||0), r = parseFloat(form.rate_tzs||0)
  return (a*r).toLocaleString('en-TZ',{minimumFractionDigits:2,maximumFractionDigits:2})
})

function handleSubmit() {
  if (!form.usdt_amount || !form.rate_tzs || !form.payment_method || !form.supplier_name) return
  emit('submit', { ...form })
}

// Expose so parent modal footer button can trigger submission
defineExpose({ submit: handleSubmit })
</script>
