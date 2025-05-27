// src/services/api.js
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'    // Pinia 예시

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,  // Vite 전용
    timeout: 5000,
})

apiClient.interceptors.request.use(config => {
    const authStore = useAuthStore()
    const token = authStore.token           // 또는 localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Token ${token}`
    }
    return config
}, error => Promise.reject(error))

export default apiClient