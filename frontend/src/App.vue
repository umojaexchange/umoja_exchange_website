<template>
  <router-view />
</template>
<script setup>
import { useUIStore } from '@/stores/ui'
const ui = useUIStore()
ui.applyTheme?.()
</script>
