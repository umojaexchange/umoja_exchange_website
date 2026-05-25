<template>
  <div class="animate-up">
    <!-- ── Stats ────────────────────────────────────────────────── -->
    <div class="stats-grid" style="margin-bottom:20px">
      <StatCard :label="t('totalPurchases')" :value="store.total"  :icon="Briefcase" color="#FACC15" :loading="store.loading" sub="All time" />
      <StatCard :label="t('totalUSDTBought')" :value="fmtN(pageSums.usdt)+' USDT'" :icon="Package" color="#3B82F6" :loading="store.loading" sub="On this page" />
      <StatCard :label="t('totalSpent')" :value="'TZS '+fmtS(pageSums.paid)"  :icon="Banknote" color="#10B981" :loading="store.loading" sub="On this page" />
      <StatCard :label="t('remainingStock')" :value="fmtN(store.inventory.total_available_usdt)+' USDT'"  :icon="ShoppingBag" color="#8B5CF6" :loading="store.loading" :sub="store.inventory.active_lots+' active lots'" />
    </div>

    <!-- ── Page header ──────────────────────────────────────────── -->
    <div class="page-header">
      <div class="page-header-left">
        <h1>{{ t('purchases') }}</h1>
        <p>{{ t('totalPurchases') }}: {{ store.total }}</p>
      </div>
      <button class="btn btn-primary" @click="openAdd">
        <svg style="width:16px;height:16px" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        {{ t('addPurchase') }}
      </button>
    </div>

    <!-- ── Table ────────────────────────────────────────────────── -->
    <div class="data-table-wrapper">
      <!-- Filters -->
      <div class="filters-bar">
        <div class="filter-search">
          <svg style="width:14px;height:14px;color:var(--text-light);flex-shrink:0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 105 11a6 6 0 0012 0z"/></svg>
          <input v-model="filters.search" :placeholder="t('search')+' '+t('supplier')+'...'" @input="debouncedFetch" />
        </div>
        <input v-model="filters.date_from" type="date" class="filter-input" @change="fetchData" />
        <input v-model="filters.date_to" type="date" class="filter-input" @change="fetchData" />
        <select v-model="filters.payment_method" class="filter-input" @change="fetchData">
          <option value="">{{ t('all') }} Methods</option>
          <option v-for="m in allMethods" :key="m.v" :value="m.v">{{ m.l }}</option>
        </select>
        <button class="btn btn-secondary btn-sm" @click="clearFilters">{{ t('clearFilters') }}</button>
        <div style="margin-left:auto;font-size:12px;color:var(--text-muted)">
          {{ t('showing') }} {{ store.items.length }} {{ t('of') }} {{ store.total }}
        </div>
      </div>

      <!-- Table -->
      <div style="overflow-x:auto">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-check"><input type="checkbox" class="table-checkbox" v-model="allSelected" @change="toggleAll" /></th>
              <th style="width:50px">#</th>
              <th>{{ t('supplier') }}</th>
              <th>{{ t('usdtAmount') }}</th>
              <th>{{ t('rateTZS') }}</th>
              <th>{{ t('amountPaid') }}</th>
              <th>Remaining</th>
              <th>{{ t('paymentMethod') }}</th>
              <th>Date</th>
              <th class="col-actions">{{ t('actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="store.loading">
              <td colspan="10" class="empty-state">
                <div class="spinner" /><span style="margin-left:10px">Loading...</span>
              </td>
            </tr>
            <tr v-else-if="!store.items.length">
              <td colspan="10">
                <div class="empty-state">
                  <div class="empty-state-icon">📭</div>
                  <div class="empty-state-text">{{ t('noData') }}</div>
                  <div class="empty-state-sub">Add your first purchase to get started</div>
                  <button class="btn btn-primary btn-sm" style="margin-top:8px" @click="openAdd">{{ t('addPurchase') }}</button>
                </div>
              </td>
            </tr>
            <tr v-for="(item, idx) in store.items" :key="item.id"
                :class="{ selected: selected.includes(item.id) }">
              <td class="col-check"><input type="checkbox" class="table-checkbox" :value="item.id" v-model="selected" /></td>
              <td style="color:var(--text-muted);font-size:12px;font-weight:600">{{ idx+1+(page-1)*pageSize }}</td>
              <td>
                <div style="font-weight:700;color:var(--text)">{{ item.supplier_name }}</div>
                <div v-if="item.notes" style="font-size:11px;color:var(--text-muted)">{{ item.notes }}</div>
              </td>
              <td><span style="font-weight:700;color:#CA8A04">{{ fmtN(item.usdt_amount) }}</span></td>
              <td>{{ fmtN(item.rate_tzs) }}</td>
              <td style="font-weight:600">{{ fmtN(item.amount_paid_tzs) }}</td>
              <td>
                <span :class="Number(item.remaining_inventory)>0?'badge badge-green':'badge badge-gray'">
                  {{ fmtN(item.remaining_inventory) }}
                </span>
              </td>
              <td><span class="badge badge-yellow">{{ item.payment_method_display }}</span></td>
              <td style="color:var(--text-muted);font-size:12px">{{ fmtDate(item.created_at) }}</td>
              <td class="col-actions">
                <div style="display:flex;align-items:center;justify-content:flex-end;gap:4px">
                  <button class="btn btn-ghost btn-icon" @click="openEdit(item)" :title="t('edit')">
                    <svg style="width:15px;height:15px" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button class="btn btn-ghost btn-icon" @click="confirmDel(item)" :title="t('delete')"
                          style="color:#EF4444" @mouseenter="e=>e.currentTarget.style.background='#FEE2E2'" @mouseleave="e=>e.currentTarget.style.background='transparent'">
                    <svg style="width:15px;height:15px" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
          <tfoot v-if="store.items.length">
            <tr>
              <td colspan="3" style="font-weight:700">Page Total</td>
              <td style="color:#CA8A04;font-weight:800">{{ fmtN(pageSums.usdt) }}</td>
              <td>—</td>
              <td style="font-weight:800">{{ fmtN(pageSums.paid) }}</td>
              <td colspan="4"></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination-bar">
        <div class="pagination-info">{{ t('showing') }} {{ (page-1)*pageSize+1 }}–{{ Math.min(page*pageSize, store.total) }} {{ t('of') }} {{ store.total }} {{ t('records') }}</div>
        <div class="pagination-controls">
          <button class="page-btn" :disabled="page<=1" @click="page--;fetchData()">‹ {{ t('previous') }}</button>
          <template v-for="p in pageButtons" :key="p">
            <span v-if="p==='...'" class="page-dots">•••</span>
            <button v-else :class="['page-btn', {active:p===page}]" @click="page=p;fetchData()">{{ p }}</button>
          </template>
          <button class="page-btn" :disabled="page>=totalPages" @click="page++;fetchData()">{{ t('next') }} ›</button>
        </div>
      </div>
    </div>

    <!-- ── Modal ─────────────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box animate-scale">
            <div class="modal-header">
              <div class="modal-title">{{ editItem ? t('editPurchase') : t('addPurchase') }}</div>
              <button class="modal-close" @click="showModal=false">✕</button>
            </div>
            <div class="modal-body">
              <PurchaseForm ref="formRef" :initial="editItem" @submit="doSubmit" />
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="showModal=false">{{ t('cancel') }}</button>
              <button class="btn btn-primary" :disabled="formLoading" @click="formRef?.submit()">
                <span v-if="formLoading" class="spinner spinner-sm" />
                {{ t('save') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Confirm Delete ─────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm=false">
          <div class="modal-box animate-scale" style="max-width:380px">
            <div class="modal-header">
              <div class="modal-title" style="color:#EF4444">⚠️ {{ t('delete') }}</div>
              <button class="modal-close" @click="showConfirm=false">✕</button>
            </div>
            <div class="modal-body">
              <p style="color:var(--text);font-weight:600;margin-bottom:8px">{{ t('deleteConfirm') }}</p>
              <p style="color:var(--text-muted);font-size:13px">{{ delTarget?.supplier_name }} — {{ fmtN(delTarget?.usdt_amount) }} USDT</p>
              <p style="color:var(--text-light);font-size:12px;margin-top:8px">{{ t('cannotUndo') }}</p>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="showConfirm=false">{{ t('cancel') }}</button>
              <button class="btn btn-danger" :disabled="delLoading" @click="doDelete">
                <span v-if="delLoading" class="spinner spinner-sm" />
                {{ t('delete') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { usePurchasesStore } from '@/stores/purchases'
import { useI18n } from '@/composables/useI18n'
import { useToast } from '@/composables/useToast'
import PurchaseForm from '@/components/purchases/PurchaseForm.vue'
import StatCard from '@/components/dashboard/KpiCard.vue'
import {
  AlertTriangle,
  Briefcase,
  Package,
  TrendingUp,
  Users,
  Sun,
  CalendarDays,
  Calendar,
  Trophy,
  BarChart2,
  PieChart,
  ShoppingCart,
  ShoppingBag,
  Banknote,
  CreditCard,
} from 'lucide-vue-next'

const store = usePurchasesStore()
const { t } = useI18n()
const toast = useToast()

// Pagination
const page = ref(1)
const pageSize = 20
const totalPages = computed(() => Math.max(1, Math.ceil(store.total / pageSize)))
const pageButtons = computed(() => {
  const total = totalPages.value, cur = page.value, pages = []
  if (total <= 7) { for (let i=1;i<=total;i++) pages.push(i); return pages }
  pages.push(1)
  if (cur > 3) pages.push('...')
  for (let i=Math.max(2,cur-1);i<=Math.min(total-1,cur+1);i++) pages.push(i)
  if (cur < total - 2) pages.push('...')
  pages.push(total)
  return pages
})

// Filters
const filters = reactive({ search:'', date_from:'', date_to:'', payment_method:'' })
const allMethods = [
  {v:'crdb',l:'CRDB'},{v:'nmb',l:'NMB'},{v:'nbc',l:'NBC'},{v:'equity',l:'Equity'},{v:'absa',l:'Absa'},
  {v:'stanbic',l:'Stanbic'},{v:'exim',l:'Exim'},{v:'boa',l:'BOA'},
  {v:'mpesa',l:'M-Pesa'},{v:'airtel',l:'Airtel'},{v:'tigo',l:'Tigo Pesa'},{v:'halopesa',l:'HaloPesa'},{v:'cash',l:'Cash'},
]

// Selection
const selected = ref([])
const allSelected = computed(() => store.items.length > 0 && selected.value.length === store.items.length)
function toggleAll() { selected.value = allSelected.value ? [] : store.items.map(i => i.id) }

// Modal state
const showModal = ref(false)
const showConfirm = ref(false)
const editItem = ref(null)
const delTarget = ref(null)
const formLoading = ref(false)
const delLoading = ref(false)
const formRef = ref(null)

// Page sums
const pageSums = computed(() => store.items.reduce((a, i) => ({
  usdt: a.usdt + Number(i.usdt_amount),
  paid: a.paid + Number(i.amount_paid_tzs),
}), { usdt:0, paid:0 }))

// Formatters
const fmtN = (v) =>
  v != null
    ? Number(v).toLocaleString('en-TZ', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    : '—'

const fmtS = (v) =>
  v != null
    ? Number(v).toLocaleString('en-TZ', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      })
    : '—'
const fmtDate = (d) => d ? new Date(d).toLocaleDateString('en-TZ',{day:'2-digit',month:'short',year:'numeric'}) : '—'

function buildParams() {
  const p = { page: page.value, page_size: pageSize }
  if (filters.search) p.search = filters.search
  if (filters.date_from) p.date_from = filters.date_from
  if (filters.date_to) p.date_to = filters.date_to
  if (filters.payment_method) p.payment_method = filters.payment_method
  return p
}

async function fetchData() { await store.fetchAll(buildParams()) }

let dt; function debouncedFetch() { clearTimeout(dt); dt = setTimeout(fetchData, 380) }

function clearFilters() { Object.assign(filters,{search:'',date_from:'',date_to:'',payment_method:''}); page.value=1; fetchData() }
function openAdd() { editItem.value=null; showModal.value=true }
function openEdit(item) { editItem.value={...item}; showModal.value=true }
function confirmDel(item) { delTarget.value=item; showConfirm.value=true }

// BUG FIX: formRef.submit() → PurchaseForm emits 'submit' → doSubmit receives data
async function doSubmit(data) {
  formLoading.value = true
  try {
    if (editItem.value) { await store.update(editItem.value.id, data); toast.success('Purchase updated') }
    else { await store.create(data); toast.success('Purchase added') }
    showModal.value = false
    store.fetchInventory()
  } catch(e) {
    toast.error(e.response?.data?.detail || Object.values(e.response?.data||{})[0]?.[0] || 'Error saving purchase')
  } finally { formLoading.value=false }
}

async function doDelete() {
  delLoading.value = true
  try { await store.remove(delTarget.value.id); toast.success('Purchase deleted'); showConfirm.value=false; store.fetchInventory() }
  catch(e) { toast.error(e.response?.data?.detail||'Cannot delete this purchase') }
  finally { delLoading.value=false }
}

onMounted(() => { fetchData(); store.fetchInventory() })
</script>

<style scoped>
.modal-enter-active,.modal-leave-active{transition:opacity .25s ease}
.modal-enter-from,.modal-leave-to{opacity:0}
.modal-enter-active .modal-box,.modal-leave-active .modal-box{transition:transform .25s ease,opacity .25s ease}
.modal-enter-from .modal-box,.modal-leave-to .modal-box{transform:scale(.95);opacity:0}
</style>
