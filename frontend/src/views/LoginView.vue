<template>
  <div class="login-bg">
    <!-- Animated orbs -->
    <div class="orb orb1" /><div class="orb orb2" /><div class="orb orb3" />
    <!-- Grid pattern -->
    <div class="grid-pattern" />

    <div class="login-wrap">
      <!-- Logo mark -->
      <div class="login-logo animate-up">
        <div class="login-logo-icon">U</div>
        <div>
          <div style="font-size:22px;font-weight:900;color:#fff;letter-spacing:1px">UMOJA</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.4);font-weight:600;letter-spacing:2px">EXCHANGE</div>
        </div>
      </div>

      <!-- Card -->
      <div class="login-card animate-up" style="animation-delay:.1s">
        <div class="login-card-header">
          <h1 class="login-title">{{ t('welcomeBack') }} 👋</h1>
          <p class="login-sub">{{ t('signInToContinue') }}</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Username -->
          <div class="form-group">
            <label class="field-label" style="color:rgba(255,255,255,0.5)">{{ t('username') }}</label>
            <div class="login-input-wrap" :class="{ focused: focusField==='user' }">
              <svg style="width:16px;height:16px;color:rgba(255,255,255,0.3);flex-shrink:0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              <input v-model="form.username" type="text" :placeholder="t('username')"
                     @focus="focusField='user'" @blur="focusField=''"
                     required autocomplete="username" class="login-input" />
            </div>
          </div>

          <!-- Password -->
          <div class="form-group">
            <label class="field-label" style="color:rgba(255,255,255,0.5)">{{ t('password') }}</label>
            <div class="login-input-wrap" :class="{ focused: focusField==='pass' }">
              <svg style="width:16px;height:16px;color:rgba(255,255,255,0.3);flex-shrink:0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
              <input v-model="form.password" :type="showPass?'text':'password'" :placeholder="t('password')"
                     @focus="focusField='pass'" @blur="focusField=''"
                     required autocomplete="current-password" class="login-input" />
              <button type="button" @click="showPass=!showPass" style="background:transparent;border:none;cursor:pointer;color:rgba(255,255,255,0.3);padding:0;transition:color .2s"
                      @mouseenter="e=>e.currentTarget.style.color='rgba(255,255,255,0.7)'"
                      @mouseleave="e=>e.currentTarget.style.color='rgba(255,255,255,0.3)'">
                <svg style="width:16px;height:16px" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path v-if="showPass" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Error -->
          <div v-if="authStore.error" class="login-error animate-fade">
            <svg style="width:15px;height:15px;flex-shrink:0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            {{ authStore.error }}
          </div>

          <!-- Submit -->
          <button type="submit" :disabled="authStore.loading" class="login-btn">
            <span v-if="authStore.loading" class="spinner spinner-sm" style="border-top-color:#0F0F0F;border-color:rgba(15,15,15,0.3)" />
            {{ authStore.loading ? t('signingIn') : t('signIn') }}
          </button>
        </form>

        <!-- Lang switcher -->
        <div style="display:flex;gap:6px;justify-content:center;margin-top:20px">
          <button v-for="l in ['en','sw']" :key="l" @click="setLang(l)"
                  :style="`padding:4px 14px;border-radius:20px;font-size:11px;font-weight:700;cursor:pointer;transition:all .2s;border:1px solid;${lang===l ? 'background:var(--yellow);color:#0F0F0F;border-color:var(--yellow)' : 'background:transparent;color:rgba(255,255,255,0.3);border-color:rgba(255,255,255,0.1)'}`">
            {{ l==='en' ? 'English' : 'Kiswahili' }}
          </button>
        </div>
      </div>

      <p style="text-align:center;color:rgba(255,255,255,0.2);font-size:12px;margin-top:24px">
        Umoja Exchange © {{ new Date().getFullYear() }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

const authStore = useAuthStore()
const { t, lang, setLang } = useI18n()
const showPass = ref(false)
const focusField = ref('')
const form = reactive({ username: '', password: '' })
async function handleLogin() { await authStore.login(form) }
</script>

<style scoped>
.login-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #0D1117 0%, #16213E 50%, #0F3460 100%);
  display: flex; align-items: center; justify-content: center;
  padding: 24px; position: relative; overflow: hidden;
}
.orb {
  position: absolute; border-radius: 50%;
  filter: blur(80px); opacity: 0.15; animation: float 8s ease-in-out infinite;
}
.orb1 { width: 400px; height: 400px; background: #FACC15; top: -100px; right: -100px; animation-delay: 0s; }
.orb2 { width: 300px; height: 300px; background: #3B82F6; bottom: -80px; left: -80px; animation-delay: -3s; }
.orb3 { width: 200px; height: 200px; background: #8B5CF6; top: 50%; left: 50%; animation-delay: -6s; }
@keyframes float { 0%,100%{transform:translateY(0) scale(1)} 50%{transform:translateY(-30px) scale(1.05)} }
.grid-pattern {
  position: absolute; inset: 0;
  background-image: linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px), linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);
  background-size: 40px 40px;
}
.login-wrap { position: relative; z-index: 1; width: 100%; max-width: 420px; display: flex; flex-direction: column; align-items: center; gap: 24px; }
.login-logo { display: flex; align-items: center; gap: 14px; }
.login-logo-icon {
  width: 52px; height: 52px; background: #FACC15; border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 22px; color: #0F0F0F;
  box-shadow: 0 8px 32px rgba(250,204,21,0.4);
}
.login-card {
  width: 100%;
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 24px; padding: 32px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.4);
}
.login-card-header { margin-bottom: 28px; }
.login-title { font-size: 22px; font-weight: 800; color: #fff; margin-bottom: 4px; }
.login-sub { font-size: 13px; color: rgba(255,255,255,0.4); }
.login-form { display: flex; flex-direction: column; gap: 16px; }
.login-input-wrap {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  transition: all 0.2s;
}
.login-input-wrap.focused { border-color: #FACC15; background: rgba(250,204,21,0.05); box-shadow: 0 0 0 3px rgba(250,204,21,0.15); }
.login-input { background: transparent; border: none; outline: none; font-size: 14px; color: #fff; width: 100%; }
.login-input::placeholder { color: rgba(255,255,255,0.25); }
.login-error {
  display: flex; align-items: center; gap: 8px; padding: 10px 14px;
  background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25);
  border-radius: 10px; color: #F87171; font-size: 13px; font-weight: 500;
}
.login-btn {
  padding: 13px; border-radius: 12px; font-size: 15px; font-weight: 700;
  background: #FACC15; color: #0F0F0F; border: none; cursor: pointer;
  transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 4px 20px rgba(250,204,21,0.3); margin-top: 4px;
}
.login-btn:hover:not(:disabled) { background: #CA8A04; box-shadow: 0 8px 30px rgba(250,204,21,0.4); transform: translateY(-1px); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
</style>
