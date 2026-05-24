import { ref } from 'vue'
const toasts = ref([])
let id = 0
function add(message, type = 'info', duration = 4000) {
  const tid = ++id
  toasts.value.push({ id: tid, message, type })
  setTimeout(() => { toasts.value = toasts.value.filter(t => t.id !== tid) }, duration)
}
export function useToast() {
  return {
    toasts,
    success: (msg) => add(msg, 'success'),
    error: (msg) => add(msg, 'error'),
    info: (msg) => add(msg, 'info'),
  }
}
