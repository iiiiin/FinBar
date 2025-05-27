<!-- src/views/Signup.vue -->
<template>
  <NavigationBar />
  <v-main>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card elevation="2">
          <v-card-title class="text-h5">회원가입</v-card-title>
          <v-card-text>
            <v-form ref="form" @submit.prevent="handleSignup">
              <v-text-field
                v-model="username"
                label="ID"
                :rules="[v => !!v || 'ID를 입력해주세요']"
                required
              />
              <v-text-field
                v-model="password1"
                label="비밀번호"
                type="password"
                required
              />
              <v-text-field
                v-model="password2"
                label="비밀번호 확인"
                type="password"
                :rules="[v => v === password1 || '비밀번호가 일치하지 않습니다']"
                required
              />
              <v-text-field
                v-model="email"
                label="이메일"
                type="email"
                :rules="[
                  v => !!v || '이메일을 입력해주세요',
                  v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || '유효한 이메일을 입력해주세요'
                ]"
                required
              />
              <!-- 나이 입력을 셀렉트 박스로 변경 -->
              <v-select
                v-model="age"
                label="연령대"
                :items="ageOptions"
                :rules="[
                  v => !!v || '나이를 입력해주세요',
                  v => v > 0 || '유효한 나이를 입력해주세요'
                ]"
                required
              />
              <v-text-field
                v-model="nickname"
                label="닉네임"
                :rules="[v => !!v || '닉네임을 입력해주세요']"
                required
              />

              <v-alert v-if="error" type="error" class="mt-4">
                {{ error }}
              </v-alert>

              <v-btn
                :loading="isSubmitting"
                :disabled="isSubmitting"
                type="submit"
                color="primary"
                block
                class="mt-4"
              >
                회원가입
              </v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <router-link to="/login">
              <v-btn text>로그인</v-btn>
            </router-link>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</v-main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/NavigationBar.vue'
import apiClient from '@/services/api'

const router = useRouter()

const username  = ref('')
const password1 = ref('')
const password2 = ref('')
const email     = ref('')
const nickname  = ref('')
const age       = ref(null)
const ageOptions = Array.from({ length: 10 }, (_, i) => (i + 1) * 10)


const isSubmitting = ref(false)
const error = ref('')

async function handleSignup() {
  if (isSubmitting.value) return
  isSubmitting.value = true
  error.value = ''

  try {
    const res = await apiClient.post('/accounts/signup/', {
      username:  username.value,
      password1: password1.value,
      password2: password2.value,
      email:     email.value,
      nickname:  nickname.value,
      age:       age.value
    })
    // console.log('signup success:', res.data)
    router.push('/login')
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.message || '회원가입 중 오류가 발생했습니다'
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
/* v-alert 전체 스타일 오버라이드 */
::v-deep .v-alert {
  background-color: #ffffff !important;       /* 흰 배경 */
  color: #000000 !important;                  /* 검은 글씨 */
  box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important; /* 연한 회색 그림자 */
  border: none !important;                    /* 테두리 제거 */
}

/* colored-border, border-start 등으로 들어온 좌측 컬러바도 제거 */
::v-deep .v-alert--border-start {
  border-left: none !important;
}

/* 만약 다른 border 속성이 붙는 경우에도 완전 제거 */
::v-deep .v-alert {
  border-width: 0 !important;
}
</style>
