import { createPinia } from 'pinia'
import { createApp } from 'vue'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

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

app.mount('#app')

