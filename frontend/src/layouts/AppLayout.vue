<template>
  <div class="app-layout">
    <div v-if="mobileOpen" class="sidebar-overlay" @click="mobileOpen=false" />

    <!-- ── SIDEBAR ──────────────────────────────────────────────── -->
    <aside :class="['sidebar', { collapsed: !expanded }, { 'mobile-open': mobileOpen }]"
           :style="{ transform: isMobile && !mobileOpen ? 'translateX(-100%)' : 'none' }">

      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-icon">U</div>
        <div class="logo-text">
          <div style="font-size:14px;font-weight:800;letter-spacing:0.5px" class="sidebar-text-primary">UMOJA</div>
          <div class="logo-sub">Exchange</div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <div class="nav-section-label">{{ t('dashboard') === 'Dashibodi' ? 'KAZI' : 'MAIN' }}</div>

        <template v-for="item in navItems" :key="item.name">
          <template v-if="item.children">
            <div class="nav-item tooltip-wrap" :class="{ active: isParentActive(item) }"
                 @click="toggleSubmenu(item.name)">
              <span class="tooltip">{{ t(item.key) }}</span>
              <span class="nav-icon" v-html="item.icon" />
              <span class="nav-label">{{ t(item.key) }}</span>
              <svg v-if="expanded" class="nav-label ml-auto"
                   style="width:14px;height:14px;transition:transform .3s;flex-shrink:0"
                   :style="{ transform: openSubmenu===item.name ? 'rotate(180deg)' : 'none' }"
                   fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </div>
            <div class="nav-sub" :style="{ maxHeight: openSubmenu===item.name&&expanded ? '200px' : '0px' }">
              <router-link v-for="child in item.children" :key="child.to" :to="child.to"
                           class="nav-sub-item" :class="{ active: $route.path===child.to }">
                {{ t(child.key) }}
              </router-link>
            </div>
          </template>

          <router-link v-else :to="item.to" class="nav-item tooltip-wrap"
                       :class="{ active: $route.name===item.routeName }"
                       @click="isMobile && (mobileOpen=false)">
            <div v-if="$route.name===item.routeName" class="nav-active-bar" />
            <span class="tooltip">{{ t(item.key) }}</span>
            <span class="nav-icon" v-html="item.icon" />
            <span class="nav-label">{{ t(item.key) }}</span>
          </router-link>
        </template>
      </nav>

      <!-- Collapse toggle -->
      <button v-if="!isMobile" @click="ui.toggleSidebar()" class="sidebar-collapse-btn">
        <svg style="width:16px;height:16px;transition:transform .3s"
             :style="{ transform: expanded ? 'rotate(180deg)' : 'none' }"
             fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
        </svg>
        <span class="nav-label" style="font-size:11px;font-weight:600">Collapse</span>
      </button>

      <!-- User -->
      <div class="sidebar-footer">
        <div class="user-card">
          <div class="user-avatar">{{ initials }}</div>
          <div class="user-info">
            <div class="user-name">{{ authStore.user?.full_name || authStore.user?.username }}</div>
            <div class="user-role">{{ authStore.user?.role }}</div>
          </div>
          <button @click.stop="authStore.logout()" title="Logout" class="sidebar-logout-btn nav-label">
            <svg style="width:16px;height:16px" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- Sidebar spacer -->
    <div v-if="!isMobile" class="sidebar-spacer" :style="{ width: expanded ? '260px' : '72px' }" />

    <!-- ── MAIN (unchanged) ─────────────────────────────────────── -->
    <div class="main-content">
      <header class="topbar">
        <button class="topbar-icon-btn" @click="isMobile ? mobileOpen=!mobileOpen : ui.toggleSidebar()">
          <svg style="width:18px;height:18px" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <div style="flex:0 0 auto">
          <div class="page-title">{{ pageTitle }}</div>
          <div class="breadcrumb">{{ formattedDate }}</div>
        </div>
        <div style="flex:1"/>
        <div class="topbar-search" style="max-width:260px">
          <svg style="width:15px;height:15px;color:var(--text-light);flex-shrink:0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 105 11a6 6 0 0012 0z"/>
          </svg>
          <input :placeholder="t('search')" />
        </div>
        <button class="topbar-icon-btn" @click="ui.toggleTheme()" :title="ui.isDark ? 'Light mode' : 'Dark mode'">
          <svg v-if="ui.isDark" style="width:17px;height:17px" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
          </svg>
          <svg v-else style="width:17px;height:17px" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
          </svg>
        </button>
        <div style="display:flex;gap:4px;background:var(--bg-input);border:1px solid var(--border);border-radius:10px;padding:4px">
          <button :class="['topbar-icon-btn lang-btn', { active: lang==='en' }]" @click="setLang('en')">EN</button>
          <button :class="['topbar-icon-btn lang-btn', { active: lang==='sw' }]" @click="setLang('sw')">SW</button>
        </div>
        <div style="display:flex;align-items:center;gap:8px;padding:6px 12px;background:var(--bg-input);border:1px solid var(--border);border-radius:10px;cursor:pointer"
             @click="authStore.logout()">
          <div style="width:28px;height:28px;background:var(--yellow);border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:12px;color:#0F0F0F">
            {{ initials }}
          </div>
          <div style="display:flex;flex-direction:column;line-height:1.2">
            <span style="font-size:12px;font-weight:700;color:var(--text)">{{ authStore.user?.username }}</span>
            <span style="font-size:10px;color:var(--text-muted);text-transform:capitalize">{{ authStore.user?.role }}</span>
          </div>
        </div>
      </header>
      <main class="page-content">
        <router-view />
      </main>
    </div>

    <ToastContainer />
  </div>
</template>


<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { useI18n } from '@/composables/useI18n'
import ToastContainer from '@/components/common/ToastContainer.vue'
import { format } from 'date-fns'

const authStore = useAuthStore()
const ui = useUIStore()
const route = useRoute()
const { t, lang, setLang } = useI18n()
const openSubmenu = ref(null)
const mobileOpen = ref(false)
const isMobile = ref(window.innerWidth < 1024)

const expanded = computed(() => ui.sidebarExpanded)

function toggleSubmenu(name) {
  openSubmenu.value = openSubmenu.value === name ? null : name
}
function isParentActive(item) {
  return item.children?.some(c => route.path.startsWith(c.to))
}

const initials = computed(() => {
  const u = authStore.user
  if (!u) return 'U'
  if (u.first_name && u.last_name) return `${u.first_name[0]}${u.last_name[0]}`
  return u.username?.[0]?.toUpperCase() || 'U'
})
const formattedDate = computed(() => format(new Date(), 'EEEE, d MMMM yyyy'))
const pageTitleMap = { dashboard:'dashboard', purchases:'purchases', sales:'sales', reports:'reports', settings:'settings' }
const pageTitle = computed(() => t(pageTitleMap[route.name] || 'dashboard'))

function handleResize() {
  isMobile.value = window.innerWidth < 1024
  if (!isMobile.value) mobileOpen.value = false
}
onMounted(() => window.addEventListener('resize', handleResize))
onUnmounted(() => window.removeEventListener('resize', handleResize))

const navItems = [
  {
    key: 'dashboard', to: '/', routeName: 'dashboard',
    icon: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width:20px;height:20px"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>`
  },
  {
    key: 'purchases', to: '/purchases', routeName: 'purchases',
    icon: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width:20px;height:20px"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"/></svg>`
  },
  {
    key: 'sales', to: '/sales', routeName: 'sales',
    icon: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width:20px;height:20px"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`
  },
  {
    key: 'reports', to: '/reports', routeName: 'reports',
    icon: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width:20px;height:20px"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>`
  },
  {
    key: 'settings', to: '/settings', routeName: 'settings',
    icon: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width:20px;height:20px"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>`
  },
]
</script>
