<template>
  <Modal :modelValue="modelValue" @update:modelValue="$emit('update:modelValue', $event)" title="Confirm Action">
    <div class="flex items-start gap-4">
      <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
      </div>
      <div>
        <p class="font-medium text-gray-900 dark:text-white">{{ message || 'Are you sure you want to proceed?' }}</p>
        <p class="text-sm text-gray-500 mt-1">This action cannot be undone.</p>
      </div>
    </div>
    <template #footer>
      <button @click="$emit('update:modelValue', false)" class="btn-secondary">Cancel</button>
      <button @click="$emit('confirm')" :disabled="loading" class="btn-danger flex items-center gap-2">
        <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
        Delete
      </button>
    </template>
  </Modal>
</template>

<script setup>
import Modal from './Modal.vue'
defineProps({ modelValue: Boolean, message: String, loading: Boolean })
defineEmits(['update:modelValue', 'confirm'])
</script>
