<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('update:modelValue', false)" />
        <div class="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col animate-slide-up">
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex-shrink-0">
            <h2 class="font-semibold text-gray-900 dark:text-white text-base">{{ title }}</h2>
            <button @click="$emit('update:modelValue', false)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <!-- Body -->
          <div class="flex-1 overflow-y-auto px-6 py-5">
            <slot />
          </div>
          <!-- Footer -->
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-100 dark:border-gray-800 flex items-center justify-end gap-3 flex-shrink-0">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({ modelValue: Boolean, title: String })
defineEmits(['update:modelValue'])
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
