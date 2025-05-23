import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth'
import axios from 'axios'

import vuetify from './plugins/vuetify'

import App from './App.vue'
import router from './router'

const pinia = createPinia()
const auth = useAuthStore(pinia)

if (auth.token) {
    axios.defaults.headers.common['Authorization'] = `Token ${auth.token}`
  }

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(vuetify)
app.mount('#app')

