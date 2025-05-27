// src/store/auth.js

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import apiClient from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(null)

  // localStorage에서 user 데이터를 안전하게 파싱
  try {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      user.value = JSON.parse(storedUser)
    }
  } catch (error) {
    console.error('사용자 데이터 파싱 실패:', error)
    localStorage.removeItem('user')
  }

  const isAuthenticated = computed(() => !!token.value)

  // 로그인
  async function login(credentials) {
    try {
      const response = await authAPI.login(credentials)
      console.log('로그인 응답:', response.data)

      // dj-rest-auth는 토큰을 key로 반환
      const newToken = response.data.key
      if (!newToken) {
        throw new Error('토큰이 응답에 포함되어 있지 않습니다.')
      }

      // 토큰 저장
      token.value = newToken
      localStorage.setItem('token', newToken)

      // axios 기본 헤더에 토큰 설정
      axios.defaults.headers.common['Authorization'] = `Token ${newToken}`
      console.log('설정된 인증 헤더:', axios.defaults.headers.common['Authorization'])

      return true
    } catch (error) {
      console.error('로그인 실패:', error)
      // 토큰 관련 데이터 초기화
      token.value = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
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
