// src/store/auth.js

import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
    user: null,
  }),
  getters: {
    // 토큰이 있으면 로그인 상태로 간주
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    setToken(token, username) {
      this.token = token
      this.username = username
      localStorage.setItem('token', token)
      localStorage.setItem('username', username)
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
    },
    clearAuth() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },
    logout() {
      axios.post('http://127.0.0.1:8000/accounts/logout/')
      this.clearAuth()
    }
  },
})
