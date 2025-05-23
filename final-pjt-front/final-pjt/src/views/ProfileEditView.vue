<!-- src/views/ProfileEdit.vue -->
<template>
    <v-container fluid class="mt-8">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="6">
          <v-card elevation="2">
            <v-card-title class="text-h5">내 정보 수정</v-card-title>
            <v-card-text>
              <v-form ref="form" @submit.prevent="handleUpdate">
                <v-text-field
                  v-model="form.username"
                  label="ID"
                  disabled
                />
                <v-text-field
                  v-model="form.email"
                  label="이메일"
                  :rules="emailRules"
                  required
                />
                <v-text-field
                  v-model="form.email"
                  label="이메일"
                  :rules="emailRules"
                  required
                />
                <!-- <v-text-field
                  v-model="form.nickname"
                  label="닉네임"
                  :rules="[v => !!v || '닉네임을 입력해주세요']"
                  required
                /> -->
                <!-- <v-text-field
                  v-model="form.age"
                  label="나이"
                  type="number"
                  :rules="ageRules"
                  required
                /> -->
  
                <v-alert v-if="error" type="error" class="mt-4">
                  {{ error }}
                </v-alert>
  
                <v-btn
                  class="mt-4"
                  color="primary"
                  block
                  :loading="loading"
                  :disabled="loading"
                  type="submit"
                >
                  저장하기
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from 'axios'
  import { useAuthStore } from '@/stores/auth'
  
  const router = useRouter()
  const auth = useAuthStore()
  
  // 폼 데이터
  const form = ref({
    username: '',
    email: '',
    // nickname: '',
    // age: '',
  })
  
  const loading = ref(false)
  const error = ref('')
  
  // 유효성 룰
  const emailRules = [
    v => !!v || '이메일을 입력해주세요',
    v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || '유효한 이메일을 입력해주세요',
  ]
  const ageRules = [
    v => !!v || '나이를 입력해주세요',
    v => (v > 0 && Number.isInteger(+v)) || '유효한 나이를 입력해주세요',
  ]
  
  // 마운트 시 프로필 정보 불러오기
  onMounted(async () => {
    loading.value = true
    try {
      // Swagger 문서의 GET /user/ 사용
      const { data } = await axios.get('http://127.0.0.1:8000/accounts/user/')
      console.log(data)
      form.value.username = data.username
      form.value.email    = data.email
    //   form.nickname = data.nickname
    //   form.age      = data.age
    } catch (e) {
      // 인증 오류 시 로그아웃 후 로그인 페이지로
      auth.clearAuth()
      router.push({ name: 'login' })
    } finally {
      loading.value = false
    }
  })
  
  // 저장 버튼 클릭 시
  async function handleUpdate() {
    if (loading.value) return
    loading.value = true
    error.value = ''
  
    try {
      // Swagger 문서의 PATCH /user/ 사용
      const { data } = await axios.patch('http://127.0.0.1:8000/accounts/user/', {
        email:    form.email,
        nickname: form.nickname,
        age:      form.age,
      })
      // Pinia에 저장된 user 정보 동기화
      auth.user = data
      router.push({ name: 'home' })
    } catch (e) {
      error.value = e.response?.data?.message || '수정 중 오류가 발생했습니다'
    } finally {
      loading.value = false
    }
  }
  console.log(form.email)
  </script>
  
  <style scoped>
  /* 추가 커스텀 스타일 필요 시 여기에 */
  </style>
  