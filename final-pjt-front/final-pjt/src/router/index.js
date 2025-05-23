import ArticleCreateView from '@/views/ArticleCreateView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import ArticleListView from '@/views/ArticleListView.vue'
import ArticleUpdateView from '@/views/ArticleUpdateView.vue'
import ErrorView from '@/views/ErrorView.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import ProfileEditView from '@/views/ProfileEditView.vue'
import SignupView from '@/views/SignupView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
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
    {
      path: '/profile',
      name: 'profile',
      component: ProfileEditView,
      meta: { requiresAuth: true }
    },
    {
      path: '/articles',
      name: 'articles',
      component: ArticleListView,
    },
    {
      path: '/articles/create',
      name: 'articleCreate',
      component: ArticleCreateView,
    },
    {
      path: '/articles/:id',
      name: 'articleDetail',
      component: ArticleDetailView,
    },
    {
      path: '/articles/:id/update',
      name: 'articleUpdate',
      component: ArticleUpdateView,
    },
    {
      path: '/error',
      name: 'error',
      component: ErrorView,
    },

  ],
})

export default router
