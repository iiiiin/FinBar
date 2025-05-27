<!-- src/views/Login.vue -->
<template>
  <NavigationBar />
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card elevation="2">
          <v-card-title class="text-h5">로그인</v-card-title>
          <v-card-text>
            <v-form ref="form" @submit.prevent="handleLogin">
              <v-text-field
                v-model="username"
                label="ID"
                :rules="[v => !!v || 'ID를 입력해주세요']"
                :error-messages="errors.username ? [errors.username] : []"
                required
              />
              <v-text-field
                v-model="password"
                label="비밀번호"
                type="password"
                :rules="[v => !!v || '비밀번호를 입력해주세요']"
                :error-messages="errors.password ? [errors.password] : []"
                required
              />

              <v-alert v-if="errors.general" type="error" class="mt-4">
                {{ errors.general }}
              </v-alert>

              <v-btn
                :loading="isSubmitting"
                :disabled="isSubmitting"
                type="submit"
                color="primary"
                block
                class="mt-4"
              >
                로그인
              </v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <router-link to="/signup">
              <v-btn text>회원가입</v-btn>
            </router-link>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import NavigationBar from '@/components/NavigationBar.vue'


const router = useRouter()
const username = ref('')
const password = ref('')
const auth = useAuthStore()

const errors = reactive({
  username: '',
  password: '',
  general: ''
})
const isSubmitting = ref(false)

function validateLogin() {
  errors.username = !username.value ? 'ID를 입력해주세요' : ''
  errors.password = !password.value ? '비밀번호를 입력해주세요' : ''
  return !errors.username && !errors.password
}

async function handleLogin() {
  if (!validateLogin()) return

  isSubmitting.value = true
  errors.general = ''

  try {
    await auth.login({
      username: username.value,
      password: password.value
    })
    router.push('/')
  } catch (err) {
    console.error('로그인 에러:', err.response?.data)
    if (err.response?.status === 400) {
      errors.general = '아이디 또는 비밀번호가 올바르지 않습니다.'
    } else if (err.response?.status === 401) {
      errors.general = '인증에 실패했습니다.'
    } else {
      errors.general = '로그인 중 오류가 발생했습니다.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* Vuetify v-btn 기본 스타일 오버라이드 */
::v-deep .v-btn {
  background-color: #ffffff !important;       /* 흰 배경 */
  color: #000000 !important;                  /* 검은 글씨 */
  box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important; /* 연한 회색 그림자 */
  border: none !important;                    /* 테두리 제거 */
}

/* Hover 시 그림자만 살짝 강조 */
::v-deep .v-btn:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

/* 선택된(primary) 혹은 text prop 은 그대로 두고, 색만 바뀌게 */
::v-deep .v-btn--text {
  background-color: transparent !important;
  box-shadow: none !important;
  color: #000000 !important;
}
</style>
