<template>
  <div class="stat-card" :style="{ '--accent-color': color }">
    <div v-if="loading" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(var(--bg-card),0.7);border-radius:inherit">
      <div class="spinner" />
    </div>
    <div style="display:flex;align-items:flex-start;justify-content:space-between">
      <div class="stat-icon" :style="{ background: color+'18' }">{{ icon }}</div>
      <div v-if="trend" class="stat-sub" :class="trend>0?'stat-trend-up':'stat-trend-down'">
        {{ trend > 0 ? '↑' : '↓' }} {{ Math.abs(trend) }}%
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
defineProps({ label: String, value: [String, Number], icon: String, color: { default: '#FACC15' }, sub: String, trend: Number, loading: Boolean })
</script>
