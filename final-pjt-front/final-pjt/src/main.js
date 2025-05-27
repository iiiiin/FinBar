import { createPinia } from 'pinia'
import { createApp } from 'vue'
import axios from 'axios'

// import vuetify from './plugins/vuetify'
import App from './App.vue'
import router from './router'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import Vue3Lottie from 'vue3-lottie'


const pinia = createPinia()
// Pinia 전역 설정
pinia.use(({ store }) => {
  store.$options = {
    ...store.$options,
    strict: false
  }
})

const vuetify = createVuetify({
  components,
  directives,
})

const app = createApp(App)
app.use(pinia)
app.use(router)
app.use(vuetify)

app.component('Lottie', Vue3Lottie)


axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL
app.config.globalProperties.$axios = axios

import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
if (authStore.token) {
  axios.defaults.headers.common['Authorization'] = `Token ${authStore.token}`
}

app.mount('#app')

