<template>
  <div class="animate-up">
    <!-- Warning -->
    <div v-if="store.summary?.capital_warning" class="warning-banner">
      <AlertTriangle :size="16" />
      {{ t('capitalWarning') }} ({{ fmt(store.summary.min_threshold) }} TZS)
    </div>

    <!-- ── KPI Cards ──────────────────────────────────────────────── -->
    <div class="stats-grid" style="margin-bottom:20px">
      <StatCard :label="t('totalCapital')" :value="'TZS '+fmtS(store.summary?.total_capital)"
        :icon="Briefcase" color="#FACC15" :loading="store.loading" sub="Company capital" />
      <StatCard :label="t('remainingInventory')" :value="fmtS(store.summary?.remaining_inventory)+' USDT'"
        :icon="Package" color="#3B82F6" :loading="store.loading" sub="Available stock" />
      <StatCard :label="t('totalProfit')" :value="'TZS '+fmtS(store.summary?.total_profit)"
        :icon="TrendingUp" color="#10B981" :loading="store.loading" sub="All time" />
      <StatCard :label="t('totalCustomers')" :value="store.summary?.total_customers??'—'"
        :icon="Users" color="#8B5CF6" :loading="store.loading" sub="Unique customers" />
    </div>

    <!-- ── Profit Period Cards ──────────────────────────────────── -->
    <div class="stats-grid" style="margin-bottom:24px">
      <StatCard :label="t('dailyProfit')" :value="'TZS '+fmtS(store.summary?.daily_profit)"
        :icon="Sun" color="#F59E0B" :loading="store.loading" :sub="t('today')" />
      <StatCard :label="t('weeklyProfit')" :value="'TZS '+fmtS(store.summary?.weekly_profit)"
        :icon="CalendarDays" color="#6366F1" :loading="store.loading" sub="Last 7 days" />
      <StatCard :label="t('monthlyProfit')" :value="'TZS '+fmtS(store.summary?.monthly_profit)"
        :icon="Calendar" color="#EC4899" :loading="store.loading" sub="This month" />
      <StatCard :label="t('annualProfit')" :value="'TZS '+fmtS(store.summary?.annual_profit)"
        :icon="Trophy" color="#14B8A6" :loading="store.loading" sub="This year" />
    </div>

    <!-- ── Charts Row 1 ─────────────────────────────────────────── -->
    <div style="display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:20px">
      <!-- Profit Trend -->
      <div class="chart-card">
        <div class="chart-card-header">
          <div>
            <div class="chart-title">{{ t('profitTrend') }}</div>
            <div class="chart-sub">{{ periodLabel }}</div>
          </div>
          <div class="period-tabs">
            <button v-for="p in periods" :key="p.key" :class="['period-tab', {active:period===p.key}]" @click="period=p.key">
              {{ t(p.key) }}
            </button>
          </div>
        </div>
        <div style="height:240px;position:relative">
          <Line v-if="trendData" :data="trendData" :options="lineOpts" />
          <div v-else class="empty-state" style="padding:40px 0">
            <div class="empty-state-icon">
              <BarChart2 :size="32" stroke-width="1.5" />
            </div>
            <div class="empty-state-text">No trend data yet</div>
          </div>
        </div>
      </div>

      <!-- Payment Doughnut -->
      <div class="chart-card">
        <div class="chart-card-header">
          <div>
            <div class="chart-title">{{ t('paymentMethods') }}</div>
            <div class="chart-sub">Sales distribution</div>
          </div>
        </div>
        <div style="height:240px;display:flex;align-items:center;justify-content:center">
          <Doughnut v-if="paymentData" :data="paymentData" :options="doughnutOpts" style="max-height:220px" />
          <div v-else class="empty-state" style="padding:40px 0">
            <div class="empty-state-icon">
              <PieChart :size="32" stroke-width="1.5" />
            </div>
            <div class="empty-state-text">No sales yet</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Monthly Bar Chart ──────────────────────────────────────── -->
    <div class="chart-card" style="margin-bottom:20px">
      <div class="chart-card-header">
        <div>
          <div class="chart-title">{{ t('monthlyOverview') }}</div>
          <div class="chart-sub">{{ t('profit') }} vs {{ t('revenue') }} — last 12 months</div>
        </div>
        <div style="display:flex;align-items:center;gap:16px">
          <div style="display:flex;align-items:center;gap:6px">
            <div style="width:10px;height:10px;border-radius:3px;background:#FACC15"/>
            <span style="font-size:11px;color:var(--text-muted);font-weight:600">{{ t('profit') }}</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <div style="width:10px;height:10px;border-radius:3px;background:#3B82F6"/>
            <span style="font-size:11px;color:var(--text-muted);font-weight:600">{{ t('revenue') }}</span>
          </div>
        </div>
      </div>
      <div style="height:220px">
        <Bar v-if="monthlyData" :data="monthlyData" :options="barOpts" />
        <div v-else class="empty-state" style="padding:40px 0">
          <div class="empty-state-icon">
            <BarChart2 :size="32" stroke-width="1.5" />
          </div>
          <div class="empty-state-text">No monthly data yet</div>
        </div>
      </div>
    </div>

    <!-- ── Bottom stats ──────────────────────────────────────────── -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
      <div v-for="s in bottomStats" :key="s.label"
           style="background:var(--bg-card);border:1px solid var(--border);border-radius:14px;padding:16px 20px;text-align:center;transition:all .2s"
           @mouseenter="e=>e.currentTarget.style.transform='translateY(-2px)'"
           @mouseleave="e=>e.currentTarget.style.transform='none'">
        <div style="display:flex;justify-content:center;margin-bottom:8px;color:var(--yellow-dark)">
          <component :is="s.icon" :size="18" />
        </div>
        <div style="font-size:24px;font-weight:800;color:var(--yellow-dark)">{{ s.value }}</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">{{ s.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line, Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
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

import { useDashboardStore } from '@/stores/dashboard'
import { useI18n } from '@/composables/useI18n'
import StatCard from '@/components/dashboard/KpiCard.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler)
ChartJS.defaults.font.family = 'Inter, sans-serif'

const store = useDashboardStore()
const { t } = useI18n()
const period = ref('monthly')
const periods = [{ key: 'daily' }, { key: 'weekly' }, { key: 'monthly' }, { key: 'annual' }]

onMounted(() => store.fetchAll())

const fmt = (v) => {
  if (v == null) return '—'

  return Number(v).toLocaleString('en-TZ', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })
}

const fmtS = (v) => {
  if (v == null) return '—'

  return Number(v).toLocaleString('en-TZ', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })
}
const periodLabel = computed(() => ({
  daily:   'Last 30 days',
  weekly:  'Last 8 weeks',
  monthly: 'Last 12 months',
  annual:  'By year',
})[period.value])

// ── Chart data  ───────────────────────────────────
const trendData = computed(() => {
  const daily   = store.charts?.daily_profit
  const monthly = store.charts?.monthly
  if (!daily?.length && !monthly?.length) return null

  let labels = [], profitData = [], revenueData = []

  if (period.value === 'daily') {
    const last7 = (daily || []).slice(-7)
    labels      = last7.map(r => r.date)
    profitData  = last7.map(r => r.profit || 0)
    revenueData = last7.map(r => r.sales  || 0)
  } else if (period.value === 'weekly') {
    const weeks = {}
    ;(daily || []).forEach(r => {
      const d = new Date(r.date)
      const ws = new Date(d); ws.setDate(d.getDate() - d.getDay())
      const key = ws.toISOString().slice(0, 10)
      if (!weeks[key]) weeks[key] = { profit: 0, sales: 0 }
      weeks[key].profit += r.profit || 0
      weeks[key].sales  += r.sales  || 0
    })
    const we = Object.entries(weeks).slice(-8)
    labels      = we.map(([k])    => 'W' + k.slice(5, 10))
    profitData  = we.map(([, v])  => v.profit)
    revenueData = we.map(([, v])  => v.sales)
  } else if (period.value === 'monthly') {
    const m     = (monthly || []).slice(-12)
    labels      = m.map(r => r.month)
    profitData  = m.map(r => r.profit || 0)
    revenueData = m.map(r => r.sales  || 0)
  } else {
    const years = {}
    ;(monthly || []).forEach(r => {
      const yr = r.month?.split(' ')[1] || '2025'
      if (!years[yr]) years[yr] = { profit: 0, sales: 0 }
      years[yr].profit += r.profit || 0
      years[yr].sales  += r.sales  || 0
    })
    const ye = Object.entries(years)
    labels      = ye.map(([k])   => k)
    profitData  = ye.map(([, v]) => v.profit)
    revenueData = ye.map(([, v]) => v.sales)
  }

  return {
    labels,
    datasets: [
      { label: t('profit'),  data: profitData,  borderColor: '#FACC15', backgroundColor: 'rgba(250,204,21,0.1)',  fill: true, tension: 0.4, pointRadius: 4, pointBackgroundColor: '#FACC15', borderWidth: 2 },
      { label: t('revenue'), data: revenueData, borderColor: '#3B82F6', backgroundColor: 'rgba(59,130,246,0.06)', fill: true, tension: 0.4, pointRadius: 4, pointBackgroundColor: '#3B82F6', borderWidth: 2 },
    ]
  }
})

const monthlyData = computed(() => {
  const m = store.charts?.monthly
  if (!m?.length) return null
  return {
    labels: m.map(r => r.month),
    datasets: [
      { label: t('profit'),  data: m.map(r => r.profit || 0), backgroundColor: '#FACC15', borderRadius: 6, borderSkipped: false },
      { label: t('revenue'), data: m.map(r => r.sales  || 0), backgroundColor: '#3B82F6', borderRadius: 6, borderSkipped: false },
    ]
  }
})

const paymentData = computed(() => {
  const d = store.charts?.payment_distribution
  if (!d?.length) return null
  const COLORS = ['#FACC15','#3B82F6','#10B981','#8B5CF6','#F59E0B','#EC4899','#14B8A6','#EF4444']
  return {
    labels: d.map(r => r.method.toUpperCase()),
    datasets: [{ data: d.map(r => r.count), backgroundColor: COLORS, borderWidth: 0, hoverOffset: 8 }]
  }
})

const bottomStats = computed(() => [
  { label: 'Total Purchases', value: store.summary?.total_purchases_count ?? 0,       icon: ShoppingCart },
  { label: 'Total Sales',     value: store.summary?.total_sales_count    ?? 0,       icon: ShoppingBag  },
  { label: 'Revenue (TZS)',   value: fmtS(store.summary?.total_sales_tzs),            icon: Banknote     },
  { label: 'Purchased (TZS)', value: fmtS(store.summary?.total_purchases_tzs),        icon: CreditCard   },
])

// ── Chart options ──────────────────────────────────────────────────
const gridColor = 'rgba(127,127,127,0.08)'
const baseOpts  = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { backgroundColor: '#1A1A2E', titleColor: '#FACC15', bodyColor: '#ccc', borderColor: 'rgba(250,204,21,0.2)', borderWidth: 1, cornerRadius: 8, padding: 12 } }
}
const lineOpts     = { ...baseOpts, plugins: { ...baseOpts.plugins, legend: { display: true, position: 'top', align: 'end', labels: { boxWidth: 10, font: { size: 11, family: 'Inter' }, padding: 16 } } }, scales: { x: { grid: { display: false }, ticks: { font: { size: 10, family: 'Inter' }, color: '#9CA3AF' } }, y: { grid: { color: gridColor, drawBorder: false }, ticks: { font: { size: 10, family: 'Inter' }, color: '#9CA3AF' } } } }
const barOpts      = { ...baseOpts, plugins: { ...baseOpts.plugins, legend: { display: false } },                                                                                                         scales: { x: { grid: { display: false }, ticks: { font: { size: 10, family: 'Inter' }, color: '#9CA3AF' } }, y: { grid: { color: gridColor, drawBorder: false }, ticks: { font: { size: 10, family: 'Inter' }, color: '#9CA3AF' } } } }
const doughnutOpts = { ...baseOpts, cutout: '68%', plugins: { ...baseOpts.plugins, legend: { display: true, position: 'bottom', labels: { boxWidth: 10, font: { size: 10, family: 'Inter' }, padding: 10 } } } }
</script>