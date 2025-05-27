// src/stores/auth.js

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api' // api.js에서 export한 authAPI 사용

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(null)
  const isAuthenticated = computed(() => !!token.value)

  // 로그인
  async function login(credentials) {
    try {
      console.log('authStore.login 호출:', credentials)
      const response = await authAPI.login(credentials)
      const newToken = response.data.key
      if (!newToken) throw new Error('토큰이 응답에 없습니다')
      token.value = newToken
      localStorage.setItem('token', newToken)
      // apiClient 인터셉터가 자동으로 헤더에 토큰을 추가함
      return true
    } catch (error) {
      clearAuth()
      throw error
    }
  }

  // 로그아웃
  async function logout() {
    try {
      await authAPI.logout()
    } catch (e) { }
    clearAuth()
  }

  // 인증 정보 초기화
  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    // apiClient 인터셉터가 있으므로 별도 헤더 삭제 불필요
  }

  // 사용자 정보 가져오기 (선택)
  async function fetchUser() {
    try {
      const response = await authAPI.getProfile()
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (e) {
      user.value = null
      localStorage.removeItem('user')
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    clearAuth,
    fetchUser,
  }
})