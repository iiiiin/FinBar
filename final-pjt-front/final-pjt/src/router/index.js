import LoginView from '@/views/LoginView.vue'
import ProfileEditView from '@/views/ProfileEditView.vue'
import SignupView from '@/views/SignupView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/signup',
      name: 'signup',
      component: SignupView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    // src/router/index.js
    {
      path: '/profile/edit',
      name: 'ProfileEdit',
      component: ProfileEditView,
      meta: { requiresAuth: true }
    },

  ],
})

export default router
