import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// API 베이스 URL 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/'

// 디버깅 모드 설정 - 개발 환경에서만 활성화
const DEBUG_MODE = import.meta.env.DEV || true

// API 설정
const API_CONFIG = {
    timeout: 5000,  // 5초 타임아웃
    retryCount: 3,  // 최대 재시도 횟수
    retryDelay: 1000,  // 재시도 간격 (1초)
}

// 디버깅 유틸리티 함수
const debug = {
    // 요청 로깅 함수
    logRequest: (config) => {
        if (!DEBUG_MODE) return

        console.group(`🚀 API 요청: ${config.method?.toUpperCase()} ${config.url}`)
        console.log('전체 URL:', `${config.baseURL}${config.url}`)
        console.log('헤더:', config.headers)
        if (config.params) console.log('쿼리 파라미터:', config.params)
        if (config.data) console.log('요청 데이터:', config.data)
        console.groupEnd()
    },

    // 응답 로깅 함수
    logResponse: (response) => {
        if (!DEBUG_MODE) return

        console.group(`✅ API 응답: ${response.config.method?.toUpperCase()} ${response.config.url}`)
        console.log('상태:', response.status, response.statusText)
        console.log('헤더:', response.headers)
        console.log('데이터:', response.data)
        console.groupEnd()
    },

    // 에러 로깅 함수
    logError: (error) => {
        if (!DEBUG_MODE) return

        console.group(`❌ API 에러: ${error.config?.method?.toUpperCase() || 'UNKNOWN'} ${error.config?.url || 'UNKNOWN'}`)
        console.error('메시지:', error.message)
        if (error.response) {
            console.error('상태:', error.response.status, error.response.statusText)
            console.error('헤더:', error.response.headers)
            console.error('데이터:', error.response.data)
        }
        console.error('전체 에러 객체:', error)
        console.groupEnd()
    }
}

// axios 인스턴스 생성
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_CONFIG.timeout,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true  // CORS 인증 요청에 필요
})

// 재시도 로직을 위한 인터셉터
api.interceptors.response.use(null, async (error) => {
    const config = error.config;

    // 재시도 횟수가 설정되지 않은 경우 초기화
    if (!config || !config.retryCount) {
        config.retryCount = API_CONFIG.retryCount;
    }

    // 재시도 가능한 에러인 경우
    if (config.retryCount > 0 && (
        error.code === 'ECONNABORTED' ||  // 타임아웃
        error.response?.status >= 500 ||   // 서버 에러
        error.response?.status === 429     // Too Many Requests
    )) {
        config.retryCount -= 1;

        // 재시도 전 대기
        await new Promise(resolve => setTimeout(resolve, API_CONFIG.retryDelay));

        // 재시도
        return api(config);
    }

    return Promise.reject(error);
});

// 요청 인터셉터 - 모든 요청에 토큰 추가
api.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore()
        const token = authStore.token

        if (token) {
            config.headers.Authorization = `Token ${token}`
        }

        // 요청 로깅
        debug.logRequest(config)
        return config
    },
    (error) => {
        debug.logError(error)
        return Promise.reject(error)
    }
)

// 응답 인터셉터 - 에러 처리
api.interceptors.response.use(
    (response) => {
        // 응답 로깅
        debug.logResponse(response)
        return response
    },
    (error) => {
        // 에러 로깅
        debug.logError(error)

        // 연결 거부 에러 처리
        if (error.code === 'ERR_CONNECTION_REFUSED') {
            console.error('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.')
        }

        // 401 에러 처리 - 인증 실패
        if (error.response?.status === 401) {
            // 프로필 관련 API는 예외 처리
            if (error.config?.url?.includes('/investment-profile/') ||
                error.config?.url?.includes('/suggests/')) {
                return Promise.reject(error)
            }

            const authStore = useAuthStore()
            authStore.clearAuth()
            router.push('/login')
        }

        // 404 에러 처리
        if (error.response?.status === 404) {
            // 프로필 관련 API는 예외 처리
            if (error.config?.url?.includes('/investment-profile/') ||
                error.config?.url?.includes('/suggests/')) {
                return Promise.reject(error)
            }
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
}

export const investmentAPI = {
    // 투자 프로필 상태 확인
    checkStatus: () => api.get('/investment-profile/status/', {
        timeout: 3000,  // 3초 타임아웃
        retryCount: 2   // 2번 재시도
    }),

    // 통합 프로필 조회
    getProfile: () => api.get('/investment-profile/profile/', {
        timeout: 5000,  // 5초 타임아웃
        retryCount: 2   // 2번 재시도
    }),

    // 투자 목표 관련
    getGoal: () => api.get('/investment-profile/goal/', {
        timeout: 3000,
        retryCount: 2
    }),

    // 투자 목표 생성
    createGoal: (data) => api.post('/investment-profile/goal/create/', data, {
        timeout: 5000,
        retryCount: 2
    }),

    // 투자 목표 수정
    updateGoal: (data) => api.patch('/investment-profile/goal/', data, {
        timeout: 5000,
        retryCount: 2
    }),

    // 투자 목표 진행 상황
    getGoalProgress: () => api.get('/investment-profile/goal/progress/', {
        timeout: 3000,
        retryCount: 2
    }),
    updateCurrentAsset: (data) => api.patch('/investment-profile/goal/update-asset/', data, {
        timeout: 5000,
        retryCount: 2
    }),

    // 투자 성향 관련
    getRiskProfile: () => api.get('/investment-profile/risk/', {
        timeout: 3000,
        retryCount: 2
    }),
    createRiskProfile: (data) => api.post('/investment-profile/risk/create/', data, {
        timeout: 5000,
        retryCount: 2
    }),
    updateRiskProfile: (data) => api.patch('/investment-profile/risk/', data, {
        timeout: 5000,
        retryCount: 2
    }),
}

export const surveyAPI = {
    // 설문 문항 조회
    getQuestions: () => api.get('/suggests/questions/'),

    // 설문 답변 제출
    submitAnswers: (data) => api.post('/suggests/submit/', data),
}

export const recommendationAPI = {
    // 추천 관련 API
    getByGoal: () => api.get('/suggests/by-goal/'),
    getDepositOnly: () => api.get('/suggests/deposit-only/'),
    getSavingOnly: () => api.get('/suggests/saving-only/'),
    saveStocks: (stocks) => api.post('/suggests/save-stocks/', { stocks }),
    getSavedRecommendations: () => api.get('/suggests/saved-recommendations/'),
    deleteSavedRecommendation: (id) => api.delete(`/suggests/saved-recommendations/${id}/`),
    deleteAllSavedRecommendations: () => api.delete('/suggests/saved-recommendations/delete-all/'),
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