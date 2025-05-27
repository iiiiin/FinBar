// main.js or main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'

import 'vuetify/styles' // Vuetify 스타일 로드
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// (✅ 아이콘 폰트 설정)
import '@mdi/font/css/materialdesignicons.css' // MDI 아이콘 포함
import { aliases, mdi } from 'vuetify/iconsets/mdi'

// Lottie
import Vue3Lottie from 'vue3-lottie'

// Vuetify 설정
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
})

// Pinia 설정
const pinia = createPinia()
pinia.use(({ store }) => {
  store.$options = {
    ...store.$options,
    strict: false,
  }
})

// 앱 생성 및 마운트
const app = createApp(App)
app.use(pinia)
app.use(router)
app.use(vuetify)
app.component('Lottie', Vue3Lottie)

// Axios 기본 설정
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL
axios.defaults.withCredentials = true

const savedToken = localStorage.getItem('token')
if (savedToken) {
  axios.defaults.headers.common['Authorization'] = `Token ${savedToken}`
}

app.config.globalProperties.$axios = axios
app.mount('#app')