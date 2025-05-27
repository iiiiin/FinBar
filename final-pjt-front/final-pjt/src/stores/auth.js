// src/store/auth.js

import { defineStore } from 'pinia'
import axios from 'axios'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    getToken: (state) => state.token,
    getUser: (state) => state.user,
  },
  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
    },
    clearAuth() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },
    setUser(user) {
      this.user = user
    },
    async logout() {
      try {
        await authAPI.logout()
      } catch (error) {
        console.error('로그아웃 API 호출 실패:', error)
      } finally {
        this.clearAuth()
      }
    },
  },
}, {
  strict: false
})
