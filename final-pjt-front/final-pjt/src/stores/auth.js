// src/store/auth.js

import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null,
  }),
  getters: {
    // 토큰이 있으면 로그인 상태로 간주
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
    },
    clearAuth() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },
    logout() {
      // 백엔드 호출이 필요하면 여기에 추가하고...
      axios.post('http://127.0.0.1:8000/accounts/logout/')
      this.clearAuth()
    }
  },
})
