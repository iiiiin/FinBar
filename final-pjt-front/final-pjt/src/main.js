import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import vuetify from './plugins/vuetify'
import App from './App.vue'
import router from './router'
import { Vue3Lottie } from 'vue3-lottie'


const pinia = createPinia()
const app = createApp(App)




app.use(pinia)
app.use(router)
app.use(vuetify)
app.component('Lottie', Vue3Lottie)

import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
if (authStore.token) {
  axios.defaults.headers.common['Authorization'] = `Token ${authStore.token}`
}
app.mount('#app')

