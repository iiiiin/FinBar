import { apiClient } from './apiClient'

// 투자 프로필 관련 API
export const investmentAPI = {
    // 투자 프로필 상태 확인
    checkStatus() {
        return apiClient.get('/investment-profile/status/')
    },

    // 투자 프로필 조회
    getProfile() {
        return apiClient.get('/investment-profile/profile/')
    },

    // 투자 목표 조회
    getGoal() {
        return apiClient.get('/investment-profile/goal/')
    },

    // 투자 목표 생성
    createGoal(data) {
        return apiClient.post('/investment-profile/goal/create/', data)
    },

    // 투자 목표 수정
    updateGoal(data) {
        return apiClient.patch('/investment-profile/goal/', data)
    },

    // 투자 목표 진행률 조회
    getGoalProgress() {
        return apiClient.get('/investment-profile/goal/progress/')
    },

    // 위험 프로필 조회
    getRiskProfile() {
        return apiClient.get('/risk-profiles/')
    },

    // 위험 프로필 생성
    createRiskProfile(data) {
        return apiClient.post('/risk-profiles/', data)
    },

    // 위험 프로필 수정
    updateRiskProfile(data) {
        return apiClient.put('/risk-profiles/', data)
    }
}

// 설문 관련 API
export const surveyAPI = {
    // 설문 문항 조회
    getQuestions() {
        return apiClient.get('/suggests/questions/')
    },

    // 설문 답변 제출
    submitAnswers(data) {
        return apiClient.post('/suggests/submit/', data)
    }
}

// 추천 관련 API
export const recommendationAPI = {
    // 추천 상품 조회
    getRecommendations() {
        return apiClient.get('/suggests/by-goal/')
    },

    // 주식 추천 저장
    saveStockRecommendation(data) {
        return apiClient.post('/suggests/save-stocks/', data)
    },

    // 저장된 추천 조회
    getSavedRecommendations() {
        return apiClient.get('/suggests/saved/')
    },

    // 저장된 추천 삭제
    deleteSavedRecommendation(id) {
        return apiClient.delete(`/suggests/saved/${id}/`)
    },

    // 모든 저장된 추천 삭제
    deleteAllSavedRecommendations() {
        return apiClient.delete('/suggests/saved/all/')
    }
} 