import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  // In production Django serves all static at /static/; dev server uses /
  base: process.env.NODE_ENV === 'production' ? '/static/' : '/',
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  build: {
    // Output into Django project so collectstatic picks it up
    outDir: '../backend/frontend_build',
    emptyOutDir: true,
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          charts: ['chart.js', 'vue-chartjs'],
          utils: ['axios', 'date-fns'],
        },
      },
    },
  },
  server: {
    port: 5173,
    // Dev: proxy API and admin to Django
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/admin': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
