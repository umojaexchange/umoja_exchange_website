<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div v-for="t in toasts" :key="t.id" :class="['toast', `toast-${t.type}`]">
          <span>{{ t.type==='success'?'✅':t.type==='error'?'❌':'ℹ️' }}</span>
          <span>{{ t.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
<script setup>
import { useToast } from '@/composables/useToast'
const { toasts } = useToast()
</script>
<style scoped>
.toast-enter-active,.toast-leave-active{transition:all .3s ease}
.toast-enter-from,.toast-leave-to{opacity:0;transform:translateX(100%)}
</style>
