import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// API 베이스 URL 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/'

// axios 인스턴스 생성
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true  // CORS 인증 요청에 필요
})

// 요청 인터셉터 - 모든 요청에 토큰 추가
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Token ${token}`
        }
        // 요청 로깅
        console.log('API 요청:', {
            method: config.method,
            url: `${config.baseURL}/${config.url}`,  // 전체 URL 로깅
            data: config.data,
            headers: config.headers
        })
        return config
    },
    (error) => {
        console.error('API 요청 에러:', error)
        return Promise.reject(error)
    }
)

// 응답 인터셉터 - 에러 처리
api.interceptors.response.use(
    (response) => {
        // 응답 로깅
        console.log('API 응답:', {
            status: response.status,
            data: response.data,
            headers: response.headers,
            url: response.config.url  // 응답 URL 로깅
        })
        return response
    },
    (error) => {
        // 에러 로깅
        console.error('API 에러:', {
            message: error.message,
            status: error.response?.status,
            data: error.response?.data,
            url: error.config?.url,  // 에러 발생 URL 로깅
            method: error.config?.method
        })

        // 연결 거부 에러 처리
        if (error.code === 'ERR_CONNECTION_REFUSED') {
            console.error('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.')
        }

        // 401 에러 처리 - 인증 실패
        if (error.response?.status === 401) {
            const authStore = useAuthStore()
            authStore.clearAuth()
            router.push('/login')
        }

        // 404 에러 처리
        if (error.response?.status === 404) {
            console.error('요청한 리소스를 찾을 수 없습니다:', error.config.url)
        }

        // 500 에러 처리
        if (error.response?.status >= 500) {
            console.error('서버 오류가 발생했습니다:', error)
        }

        return Promise.reject(error)
    }
)

// API 엔드포인트들
export const authAPI = {
    // 로그인
    login: (credentials) => api.post('/accounts/login/', credentials),

    // 회원가입
    signup: (userData) => api.post('/accounts/signup/', userData),

    // 로그아웃
    logout: () => api.post('/accounts/logout/'),

    // 사용자 정보 조회
    getProfile: () => api.get('/accounts/profile/'),

    // 사용자 정보 수정
    updateProfile: (data) => api.patch('/accounts/profile/', data),
}

export const investmentAPI = {
    // 투자 프로필 상태 확인
    checkStatus: () => api.get('/investment-profile/status/'),

    // 통합 프로필 조회
    getProfile: () => api.get('/investment-profile/profile/'),

    // 투자 목표 관련
    getGoal: () => api.get('/investment-profile/goal/'),
    createGoal: (data) => api.post('/investment-profile/goal/create/', data),
    updateGoal: (data) => api.patch('/investment-profile/goal/', data),

    // 투자 목표 진행 상황
    getGoalProgress: () => api.get('/investment-profile/goal/progress/'),
    updateCurrentAsset: (data) => api.patch('/investment-profile/goal/update-asset/', data),

    // 투자 성향 관련
    getRiskProfile: () => api.get('/investment-profile/risk/'),
    createRiskProfile: (data) => api.post('/investment-profile/risk/create/', data),
    updateRiskProfile: (data) => api.patch('/investment-profile/risk/', data),
}

export const surveyAPI = {
    // 설문 문항 조회
    getQuestions: () => api.get('/suggests/questions/'),

    // 설문 답변 제출
    submitAnswers: (data) => api.post('/suggests/submit/', data),
}

export const recommendationAPI = {
    // 메인 추천 (목표 기반)
    getByGoal: (params) => api.get('/suggests/by-goal/', { params }),

    // 예금만 추천
    getDepositOnly: (requiredReturn) =>
        api.get('/suggests/deposit-only/', { params: { required_return: requiredReturn } }),

    // 적금만 추천
    getSavingOnly: (requiredReturn) =>
        api.get('/suggests/saving-only/', { params: { required_return: requiredReturn } }),

    // 주식 추천 저장
    saveStocks: (stocks) => api.post('/suggests/save-stocks/', stocks),
}

export const productAPI = {
    // 예금 상품 목록
    getDeposits: (params) => api.get('/financial-products/deposits/', { params }),

    // 예금 상품 상세
    getDepositDetail: (id) => api.get(`/financial-products/deposits/${id}/`),

    // 적금 상품 목록
    getSavings: (params) => api.get('/financial-products/savings/', { params }),

    // 적금 상품 상세
    getSavingDetail: (id) => api.get(`/financial-products/savings/${id}/`),

    // 북마크 관련
    bookmarkDeposit: (id) => api.post(`/my-products/deposits/${id}/bookmark/`),
    unbookmarkDeposit: (id) => api.delete(`/my-products/deposits/${id}/bookmark/`),
    bookmarkSaving: (id) => api.post(`/my-products/savings/${id}/bookmark/`),
    unbookmarkSaving: (id) => api.delete(`/my-products/savings/${id}/bookmark/`),

    // 북마크 목록
    getBookmarkedDeposits: () => api.get('/my-products/deposits/'),
    getBookmarkedSavings: () => api.get('/my-products/savings/'),
}

export const articleAPI = {
    // 게시글 목록
    getArticles: (params) => api.get('/articles/', { params }),

    // 게시글 생성
    createArticle: (data) => api.post('/articles/', data),

    // 게시글 상세
    getArticle: (id) => api.get(`/articles/${id}/`),

    // 게시글 수정
    updateArticle: (id, data) => api.patch(`/articles/${id}/`, data),

    // 게시글 삭제
    deleteArticle: (id) => api.delete(`/articles/${id}/`),

    // 댓글 생성
    createComment: (articleId, data) => api.post(`/articles/${articleId}/comments/`, data),

    // 댓글 수정
    updateComment: (articleId, commentId, data) =>
        api.patch(`/articles/${articleId}/comments/${commentId}/`, data),

    // 댓글 삭제
    deleteComment: (articleId, commentId) =>
        api.delete(`/articles/${articleId}/comments/${commentId}/`),
}

export const externalAPI = {
    // 주변 은행 검색
    searchBanks: (params) => api.get('/external/banks/', { params }),

    // 현물 가격
    getSpotPrices: () => api.get('/external/spot-prices/'),

    // YouTube 영상 검색
    searchVideos: (query) => api.get('/external/videos/', { params: { q: query } }),
}

// 기본 export
export default api 