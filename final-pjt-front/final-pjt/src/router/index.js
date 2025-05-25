import ArticleCreateView from '@/views/ArticleCreateView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import ArticleListView from '@/views/ArticleListView.vue'
import ArticleUpdateView from '@/views/ArticleUpdateView.vue'
import BankMapView from '@/views/BankMapView.vue'
import DepositDetailView from '@/views/DepositDetailView.vue'
import DepositListView from '@/views/DepositListView.vue'
import ErrorView from '@/views/ErrorView.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import ProfileEditView from '@/views/ProfileEditView.vue'
import SignupView from '@/views/SignupView.vue'
import SpotPriceView from '@/views/SpotPriceView.vue'
import StockVideoView from '@/views/StockVideoView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 랜딩 페이지
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    // 회원가입 페이지
    {
      path: '/signup',
      name: 'signup',
      component: SignupView,
    },
    // 로그인 페이지
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    // 회원정보 수정 페이지
    {
      path: '/profile',
      name: 'profile',
      component: ProfileEditView,
      meta: { requiresAuth: true }
    },
    // 커뮤니티 게시글 목록 페이지
    {
      path: '/articles',
      name: 'articles',
      component: ArticleListView,
    },
    // 커뮤니티 게시글 생성 페이지
    {
      path: '/articles/create',
      name: 'articleCreate',
      component: ArticleCreateView,
    },
    // 커뮤니티 게시글 상세 페이지
    {
      path: '/articles/:id',
      name: 'articleDetail',
      component: ArticleDetailView,
    },
    // 커뮤니티 게시글 수정 페이지
    {
      path: '/articles/:id/update',
      name: 'articleUpdate',
      component: ArticleUpdateView,
    },
    // 에러 페이지
    {
      path: '/error',
      name: 'error',
      component: ErrorView,
    },
    // 주식정보(영상)검색 페이지
    {
      path: '/videostock',
      name: 'videoStock',
      component: StockVideoView,
    },
    // 주변 은행 검색 페이지
    {
      path: '/bankmap',
      name: 'bankMap',
      component: BankMapView,
    },
    // 현물 상품 변동 페이지
    {
      path: '/spotPrice',
      name: 'spotPrice',
      component: SpotPriceView,
    },
    // 예적금 상품 목록 페이지
    {
      path: '/depositlist',
      name: 'depositList',
      component: DepositListView,
    },
    // 예적금 상품 상세 페이지
    {
      path: '/depositdetail',
      name: 'depositDetail',
      component: DepositDetailView,
    },
  ],
})

export default router
