// src/store/auth.js

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)

  // 로그인
  async function login(credentials) {
    try {
      const response = await authAPI.login(credentials)
      const { token: newToken, user: userData } = response.data

      // 토큰과 사용자 정보 저장
      token.value = newToken
      user.value = userData

      // localStorage에 저장
      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify(userData))

      axios.defaults.headers.common['Authorization'] = `Token ${newToken}`
      return true
    } catch (error) {
      console.error('로그인 실패:', error)
      throw error
    }
  }

  // 로그아웃
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  }

  // 인증 정보 초기화
  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    clearAuth
  }
})
