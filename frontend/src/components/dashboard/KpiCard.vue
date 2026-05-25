<template>
  <div class="stat-card" :style="{ '--accent-color': color }">
    <div v-if="loading" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(var(--bg-card),0.7);border-radius:inherit">
      <div class="spinner" />
    </div>
    <div style="display:flex;align-items:flex-start;justify-content:space-between">
      <div class="stat-icon" :style="{ background: color+'18', color }">
        <component :is="icon" :size="20" :stroke-width="1.8" />
      </div>
      <div v-if="trend" class="stat-sub" :class="trend>0?'stat-trend-up':'stat-trend-down'">
        <TrendingUp v-if="trend>0" :size="12" />
        <TrendingDown v-else :size="12" />
        {{ Math.abs(trend) }}%
      </div>
    </div>
    <div>
      <div class="stat-label">{{ label }}</div>
      <div class="stat-value">{{ value }}</div>
    </div>
    <div v-if="sub" class="stat-sub">{{ sub }}</div>
  </div>
</template>

<script setup>
import { TrendingUp, TrendingDown } from 'lucide-vue-next'

defineProps({
  label:   String,
  value:   [String, Number],
  icon:    { type: [Object, Function] },
  color:   { default: '#FACC15' },
  sub:     String,
  trend:   Number,
  loading: Boolean,
})
</script>