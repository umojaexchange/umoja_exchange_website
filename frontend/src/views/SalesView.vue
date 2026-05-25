<template>
  <div class="animate-up">
    <!-- ── Stats ────────────────────────────────────────────────── -->
    <div class="stats-grid" style="margin-bottom:20px">
      <StatCard :label="t('totalSales')" :value="store.total" :icon="CreditCard" color="#FACC15" :loading="store.loading" sub="All time" />
      <StatCard :label="t('totalUSDTSold')" :value="fmtN(pageSums.usdt)+' USDT'" :icon="Package" color="#10B981" :loading="store.loading" sub="On this page" />
      <StatCard :label="t('totalRevenue')" :value="'TZS '+fmtS(pageSums.paid)" :icon="Trophy" color="#3B82F6" :loading="store.loading" sub="On this page" />
      <StatCard :label="t('totalProfit')" :value="'TZS '+fmtS(pageSums.profit)" :icon="Banknote" color="#8B5CF6" :loading="store.loading" :sub="pageSums.profit>0?'Positive':'Check rates'" />
    </div>

    <!-- ── Page header ──────────────────────────────────────────── -->
    <div class="page-header">
      <div class="page-header-left">
        <h1>{{ t('sales') }}</h1>
        <p>FIFO-based USDT sales to customers</p>
      </div>
      <button class="btn btn-primary" @click="showModal=true">
        <svg style="width:16px;height:16px" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        {{ t('newSale') }}
      </button>
    </div>

    <!-- ── Table ────────────────────────────────────────────────── -->
    <div class="data-table-wrapper">
      <div class="filters-bar">
        <div class="filter-search">
          <svg style="width:14px;height:14px;color:var(--text-light);flex-shrink:0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 105 11a6 6 0 0012 0z"/></svg>
          <input v-model="filters.search" :placeholder="t('search')+' '+t('customer')+'...'" @input="debouncedFetch" />
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

      <div style="overflow-x:auto">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-check"><input type="checkbox" class="table-checkbox" /></th>
              <th style="width:50px">#</th>
              <th>{{ t('customer') }}</th>
              <th>USDT</th>
              <th>Sale Rate</th>
              <th>Paid (TZS)</th>
              <th>{{ t('avgBuyRate') }}</th>
              <th>{{ t('profitMargin') }}</th>
              <th style="color:#10B981">Profit (TZS)</th>
              <th>Method</th>
              <th>Date</th>
              <th class="col-actions">{{ t('actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="store.loading">
              <td colspan="12" class="empty-state">
                <div class="spinner" /><span style="margin-left:10px">Loading...</span>
              </td>
            </tr>
            <tr v-else-if="!store.items.length">
              <td colspan="12">
                <div class="empty-state">
                  <div class="empty-state-icon">💸</div>
                  <div class="empty-state-text">{{ t('noData') }}</div>
                  <div class="empty-state-sub">Create your first sale</div>
                  <button class="btn btn-primary btn-sm" style="margin-top:8px" @click="showModal=true">{{ t('newSale') }}</button>
                </div>
              </td>
            </tr>
            <tr v-for="(item, idx) in store.items" :key="item.id" style="cursor:pointer"
                @click="viewDetail(item)">
              <td class="col-check" @click.stop><input type="checkbox" class="table-checkbox" /></td>
              <td style="color:var(--text-muted);font-size:12px;font-weight:600">{{ idx+1+(page-1)*pageSize }}</td>
              <td>
                <div style="font-weight:700;color:var(--text)">{{ item.customer_name }}</div>
                <div v-if="item.notes" style="font-size:11px;color:var(--text-muted)">{{ item.notes }}</div>
              </td>
              <td style="font-weight:700;color:#CA8A04">{{ fmtN(item.usdt_amount) }}</td>
              <td>{{ fmtN(item.sale_rate_tzs) }}</td>
              <td style="font-weight:600">{{ fmtN(item.paid_amount_tzs) }}</td>
              <td style="color:var(--text-muted)">{{ fmtN(item.avg_buy_rate) }}</td>
              <td>
                <span :class="Number(item.profit_margin)>=0?'badge badge-green':'badge badge-red'">{{ fmtN(item.profit_margin) }}</span>
              </td>
              <td>
                <span style="font-weight:800" :style="{color:Number(item.profit_tzs)>=0?'#16A34A':'#DC2626'}">
                  {{ fmtN(item.profit_tzs) }}
                </span>
              </td>
              <td><span class="badge badge-yellow">{{ item.payment_method_display }}</span></td>
              <td style="color:var(--text-muted);font-size:12px">{{ fmtDate(item.created_at) }}</td>
              <td class="col-actions" @click.stop>
                <button  class="btn btn-ghost btn-icon" @click.stop="confirmDel(item)" style="color:#EF4444">
                  <svg style="width:15px;height:15px" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </td>
            </tr>
          </tbody>
          <tfoot v-if="store.items.length">
            <tr>
              <td colspan="2"></td>
              <td style="font-weight:700">Page Total</td>
              <td style="color:#CA8A04;font-weight:800">{{ fmtN(pageSums.usdt) }}</td>
              <td>—</td>
              <td style="font-weight:800">{{ fmtN(pageSums.paid) }}</td>
              <td>—</td><td>—</td>
              <td style="font-weight:800;color:#16A34A">{{ fmtN(pageSums.profit) }}</td>
              <td colspan="3"></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination-bar">
        <div class="pagination-info">{{ t('showing') }} {{ Math.min((page-1)*pageSize+1,store.total) }}–{{ Math.min(page*pageSize,store.total) }} {{ t('of') }} {{ store.total }}</div>
        <div class="pagination-controls">
          <button class="page-btn" :disabled="page<=1" @click="page--;fetchData()">‹ {{ t('previous') }}</button>
          <template v-for="p in pageButtons" :key="p">
            <span v-if="p==='...'" class="page-dots">•••</span>
            <button v-else :class="['page-btn',{active:p===page}]" @click="page=p;fetchData()">{{ p }}</button>
          </template>
          <button class="page-btn" :disabled="page>=totalPages" @click="page++;fetchData()">{{ t('next') }} ›</button>
        </div>
      </div>
    </div>

    <!-- ── Create Modal ──────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
          <div class="modal-box animate-scale">
            <div class="modal-header">
              <div class="modal-title">{{ t('newSale') }}</div>
              <button class="modal-close" @click="showModal=false">✕</button>
            </div>
            <div class="modal-body">
              <SaleForm ref="saleFormRef" @submit="doCreate" />
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="showModal=false">{{ t('cancel') }}</button>
              <button class="btn btn-primary" :disabled="formLoading" @click="saleFormRef?.submit()">
                <span v-if="formLoading" class="spinner spinner-sm" />
                Execute Sale
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Detail Modal ──────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDetail" class="modal-overlay" @click.self="showDetail=false">
          <div class="modal-box animate-scale" style="max-width:560px">
            <div class="modal-header">
              <div class="modal-title">{{ t('fifoBreakdown') }} — Sale #{{ detailItem?.id }}</div>
              <button class="modal-close" @click="showDetail=false">✕</button>
            </div>
            <div class="modal-body" v-if="detailItem">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
                <div v-for="s in detailStats" :key="s.label" style="padding:12px;background:var(--bg-input);border-radius:12px;border:1px solid var(--border)">
                  <div style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">{{ s.label }}</div>
                  <div style="font-size:16px;font-weight:800" :style="{color:s.color||'var(--text)'}">{{ s.value }}</div>
                </div>
              </div>
              <div v-if="detailItem.sale_lots?.length">
                <div style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">FIFO Lots Consumed</div>
                <div v-for="lot in detailItem.sale_lots" :key="lot.id"
                     style="display:flex;justify-content:space-between;padding:10px 14px;background:var(--bg-input);border-radius:10px;margin-bottom:6px;border:1px solid var(--border);font-size:13px">
                  <span style="color:var(--text-muted)">Lot #{{ lot.inventory_lot }} (Purchase #{{ lot.purchase_id }})</span>
                  <span style="font-weight:700">{{ fmtN(lot.usdt_consumed) }} USDT @ {{ fmtN(lot.buy_rate) }}</span>
                </div>
              </div>
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
            <div class="modal-header"><div class="modal-title" style="color:#EF4444">⚠️ Delete Sale</div><button class="modal-close" @click="showConfirm=false">✕</button></div>
            <div class="modal-body">
              <p style="color:var(--text);font-weight:600;margin-bottom:8px">{{ t('deleteConfirm') }}</p>
              <p style="color:var(--text-muted);font-size:13px">{{ delTarget?.customer_name }} — {{ fmtN(delTarget?.usdt_amount) }} USDT</p>
              <p style="color:#F59E0B;font-size:12px;margin-top:8px">⚠️ Inventory will be restored via FIFO reversal.</p>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="showConfirm=false">{{ t('cancel') }}</button>
              <button class="btn btn-danger" :disabled="delLoading" @click="doDelete">
                <span v-if="delLoading" class="spinner spinner-sm" />{{ t('delete') }}
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
import { useSalesStore } from '@/stores/sales'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'
import { useToast } from '@/composables/useToast'
import SaleForm from '@/components/sales/SaleForm.vue'
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

const store = useSalesStore()
const authStore = useAuthStore()
const { t } = useI18n()
const toast = useToast()

const page = ref(1); const pageSize = 20
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

const filters = reactive({ search:'', date_from:'', date_to:'', payment_method:'' })
const allMethods = [
  {v:'crdb',l:'CRDB'},{v:'nmb',l:'NMB'},{v:'nbc',l:'NBC'},{v:'equity',l:'Equity'},{v:'absa',l:'Absa'},
  {v:'stanbic',l:'Stanbic'},{v:'exim',l:'Exim'},{v:'boa',l:'BOA'},
  {v:'mpesa',l:'M-Pesa'},{v:'airtel',l:'Airtel'},{v:'tigo',l:'Tigo Pesa'},{v:'halopesa',l:'HaloPesa'},{v:'cash',l:'Cash'},
]

const showModal = ref(false)
const showDetail = ref(false)
const showConfirm = ref(false)
const detailItem = ref(null)
const delTarget = ref(null)
const formLoading = ref(false)
const delLoading = ref(false)
const saleFormRef = ref(null)

const pageSums = computed(() => store.items.reduce((a, i) => ({
  usdt: a.usdt + Number(i.usdt_amount),
  paid: a.paid + Number(i.paid_amount_tzs),
  profit: a.profit + Number(i.profit_tzs),
}), { usdt:0, paid:0, profit:0 }))

const detailStats = computed(() => detailItem.value ? [
  { label: 'Customer', value: detailItem.value.customer_name },
  { label: 'USDT Sold', value: fmtN(detailItem.value.usdt_amount), color: '#CA8A04' },
  { label: 'Sale Rate', value: fmtN(detailItem.value.sale_rate_tzs)+' TZS' },
  { label: 'Avg Buy Rate', value: fmtN(detailItem.value.avg_buy_rate)+' TZS' },
  { label: 'Profit Margin', value: fmtN(detailItem.value.profit_margin)+' TZS', color: '#16A34A' },
  { label: 'Total Profit', value: 'TZS '+fmtN(detailItem.value.profit_tzs), color: '#16A34A' },
] : [])
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
function viewDetail(item) { detailItem.value=item; showDetail.value=true }
function confirmDel(item) { delTarget.value=item; showConfirm.value=true }

async function doCreate(data) {
  formLoading.value = true
  try { await store.create(data); toast.success('Sale executed successfully'); showModal.value=false }
  catch(e) { toast.error(e.response?.data?.detail || Object.values(e.response?.data||{})[0]?.[0] || 'Sale failed') }
  finally { formLoading.value=false }
}

async function doDelete() {
  delLoading.value = true
  try { await store.remove(delTarget.value.id); toast.success('Sale deleted, inventory restored'); showConfirm.value=false }
  catch(e) { toast.error(e.response?.data?.detail||'Cannot delete sale') }
  finally { delLoading.value=false }
}
onMounted(fetchData)
</script>
<style scoped>
.modal-enter-active,.modal-leave-active{transition:opacity .25s ease}
.modal-enter-from,.modal-leave-to{opacity:0}
.modal-enter-active .modal-box,.modal-leave-active .modal-box{transition:transform .25s ease,opacity .25s ease}
.modal-enter-from .modal-box,.modal-leave-to .modal-box{transform:scale(.95);opacity:0}
</style>
