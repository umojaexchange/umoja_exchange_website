import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const sidebarExpanded = ref(window.innerWidth >= 1024)
  const isDark = ref(localStorage.getItem('umoja_theme') === 'dark')

  function toggleSidebar() { sidebarExpanded.value = !sidebarExpanded.value }
  function setSidebar(v) { sidebarExpanded.value = v }

  function applyTheme() {
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  function toggleTheme() {
    isDark.value = !isDark.value
    localStorage.setItem('umoja_theme', isDark.value ? 'dark' : 'light')
    applyTheme()
  }

  applyTheme()
  watch(isDark, applyTheme)

  return { sidebarExpanded, isDark, toggleSidebar, setSidebar, toggleTheme, applyTheme }
})
