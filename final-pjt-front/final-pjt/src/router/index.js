import ArticleCreateView from '@/views/ArticleCreateView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import ArticleListView from '@/views/ArticleListView.vue'
import ArticleUpdateView from '@/views/ArticleUpdateView.vue'
import BankMapView from '@/views/BankMapView.vue'
import DepositDetailView from '@/views/DepositDetailView.vue'
import ErrorView from '@/views/ErrorView.vue'
import MenuView from '@/views/MenuView.vue'
import LoginView from '@/views/LoginView.vue'
import ProfileEditView from '@/views/ProfileEditView.vue'
import SignupView from '@/views/SignupView.vue'
import SpotPriceView from '@/views/SpotPriceView.vue'
import StockVideoView from '@/views/StockVideoView.vue'
import VideoDetailView from '@/views/VideoDetailView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import ProductListView from '@/views/ProductListView.vue'
import SavingDetailView from '@/views/SavingDetailView.vue'
import RecommendationPageView from '@/views/RecommendationPageView.vue'
import SurveyPageView from '@/views/SurveyPageView.vue'
import InvestmentProfileView from '@/views/InvestmentProfileView.vue'
import InvestmentGoalView from '@/views/InvestmentGoalView.vue'
import { investmentAPI } from '@/services/api'
import HomeView from '@/views/HomeView.vue'
import ProfileView from '@/views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    // 랜딩 페이지
    {
      path: '/menu',
      name: 'menu',
      component: MenuView,
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
      component: ProfileView,
    },
    // 회원정보 수정 페이지
    {
      path: '/profileedit',
      name: 'profileEdit',
      component: ProfileEditView,
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
    // 주식정보(영상) 검색 페이지
    {
      path: '/videostock',
      name: 'videoStock',
      component: StockVideoView,
    },
    // 주식정보(영상) 상세 페이지
    {
      path: '/videostock/:id',
      name: 'videoDetail',
      component: VideoDetailView,
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
      path: '/product',
      name: 'productList',
      component: ProductListView,
    },
    // 예금 상품 상세 페이지
    {
      path: '/deposits/:id',
      name: 'depositDetail',
      component: DepositDetailView,
    },
    // 예금 상품 상세 페이지
    {
      path: '/savings/:id',
      name: 'savingDetail',
      component: SavingDetailView,
    },
    //투자 성향 설문 
    {
      path: '/survey',
      name: 'survey',
      component: SurveyPageView,
      meta: { requiresAuth: true }
    },
    // 추천 페이지 
    {
      path: '/recommendations',
      name: 'recommendations',
      component: RecommendationPageView,
      meta: {
        requiresAuth: true,
        requiresProfile: true  // 프로필 완성 필요
      }
    },
    // 투자 프로필 페이지 라우트 추가
    {
      path: '/investment-profile',
      name: 'investmentProfile',
      component: InvestmentProfileView,
      meta: { requiresAuth: true }  // 로그인 필요
    },
    // 투자 목표 설정 페이지
    {
      path: '/investment-goal',
      name: 'investmentGoal',
      component: InvestmentGoalView,
      meta: { requiresAuth: true }  // 로그인 필요
    }
  ],
})

// 네비게이션 가드 추가
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')

  // 인증이 필요한 페이지 체크
  if (to.meta.requiresAuth && !token) {
    next({ name: 'login' })
    return
  }

  // 프로필 완성이 필요한 페이지 체크
  if (to.meta.requiresProfile && token) {
    try {
      const { data } = await investmentAPI.checkStatus()

      if (!data.has_investment_profile || !data.has_investment_goal) {
        next({ name: 'investmentProfile' })
        return
      }
    } catch (error) {
      console.error('프로필 상태 확인 실패:', error)
      next({ name: 'investmentProfile' })
      return
    }
  }

  next()
})

export default router
