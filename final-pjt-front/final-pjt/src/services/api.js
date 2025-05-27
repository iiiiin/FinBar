// src/services/api.js
import axios from 'axios';

// Axios 인스턴스 설정
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 5000,
});

// 인증 토큰 자동 추가 (인터셉터)
apiClient.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
}, error => Promise.reject(error));

// API 모듈들 정의
export const authAPI = {
    login: (credentials) => apiClient.post('/accounts/login/', credentials),
    signup: (userData) => apiClient.post('/accounts/signup/', userData),
    logout: () => apiClient.post('/accounts/logout/'),
    getProfile: () => apiClient.get('/accounts/profile/'),
};

export const investmentAPI = {
    checkStatus: () => apiClient.get('/investment-profile/status/'),
    getProfile: () => apiClient.get('/investment-profile/profile/'),
    getGoal: () => apiClient.get('/investment-profile/goal/'),
    createGoal: (data) => apiClient.post('/investment-profile/goal/create/', data),
    updateGoal: (data) => apiClient.patch('/investment-profile/goal/', data),
    getGoalProgress: () => apiClient.get('/investment-profile/goal/progress/'),
    updateCurrentAsset: (data) => apiClient.patch('/investment-profile/goal/update-asset/', data),
    getRiskProfile: () => apiClient.get('/investment-profile/risk/'),
    createRiskProfile: (data) => apiClient.post('/investment-profile/risk/create/', data),
    updateRiskProfile: (data) => apiClient.patch('/investment-profile/risk/', data),
};

export const surveyAPI = {
    getQuestions: () => apiClient.get('/suggests/questions/'),
    submitAnswers: (data, headers = {}) => apiClient.post('/suggests/submit/', data, { headers }),
};

export const recommendationAPI = {
    getByGoal: () => apiClient.get('/suggests/by-goal/', { timeout: 20000 }),
    getDepositOnly: () => apiClient.get('/suggests/deposit-only/'),
    getSavingOnly: () => apiClient.get('/suggests/saving-only/'),
    saveStocks: (stocks) => apiClient.post('/suggests/save-stocks/', { stocks }),
    getSavedRecommendations: () => apiClient.get('/suggests/saved-recommendations/'),
    deleteSavedRecommendation: (id) => apiClient.delete(`/suggests/saved-recommendations/${id}/`),
    deleteAllSavedRecommendations: () => apiClient.delete('/suggests/saved-recommendations/delete-all/'),
};

// 기본 export
export default apiClient;
