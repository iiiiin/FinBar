<template>
  <v-container fluid class="mt-8">
    <!-- 네비게이션 바 -->
    <v-row>
      <v-col cols="12">
        <NavigationBar />
      </v-col>
    </v-row>

    <!-- 프로필 수정 폼 -->
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card elevation="2">
          <v-card-title class="text-h5">내 정보 수정</v-card-title>
          <v-card-text>
            <!-- 기본 정보 수정 폼 -->
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
                v-model="form.nickname"
                label="닉네임"
                :rules="nicknameRules"
                required
              />
              <v-select
              v-model="form.age"
              label="연령대"
              :items="ageOptions"
              :rules="ageRules"
              required
              />
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

            <!-- 비밀번호 변경 섹션 -->
            <v-divider class="my-4" />
            <div class="text-subtitle-1 mb-2">비밀번호 변경</div>
            <v-form ref="pwdForm" @submit.prevent="PasswordUpdate">
              <v-text-field
                v-model="passwordNew"
                label="새 비밀번호"
                type="password"
                :rules="passwordRules"
              />
              <v-text-field
                v-model="passwordConfirm"
                label="새 비밀번호 확인"
                type="password"
                :rules="[v => v === passwordNew || '비밀번호가 일치하지 않습니다']"
              />
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
                변경하기
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
import NavigationBar from '@/components/NavigationBar.vue'

const router = useRouter()
const auth = useAuthStore()

// 폼 데이터
const form = ref({
  username: '',
  email: '',
  nickname: '',
  age: '',
})
const passwordNew     = ref('')
const passwordConfirm = ref('')

const loading = ref(false)
const error   = ref('')

// 유효성 룰
const emailRules    = [v => !!v || '이메일을 입력해주세요', v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || '유효한 이메일을 입력해주세요']
const nicknameRules = [v => !!v || '닉네임을 입력해주세요']
const ageRules      = [v => !!v || '연령대를 입력해주세요', v => v > 0 && Number.isInteger(+v) || '유효한 연령대를 입력해주세요']
const passwordRules = [v => !passwordNew.value || v.length >= 6 || '새 비밀번호는 최소 6자리 이상이어야 합니다']
const ageOptions = Array.from({ length: 10 }, (_, i) => (i + 1) * 10)

// 마운트 시 프로필 정보 불러오기
onMounted(async () => {
  loading.value = true
  try {
    const { data } = await axios.get('http://127.0.0.1:8000/accounts/user/')
    form.value.username = data.username
    form.value.email    = data.email
    form.value.nickname = data.nickname
    form.value.age      = data.age
  } catch (e) {
    auth.clearAuth()
    router.push({ name: 'login' })
  } finally {
    loading.value = false
  }
})

// 기본 정보 수정
async function handleUpdate() {
  if (loading.value) return
  loading.value = true
  error.value   = ''
  try {
    const { data } = await axios.patch('http://127.0.0.1:8000/accounts/user/', {
      email:    form.value.email,
      nickname: form.value.nickname,
      age:      form.value.age,
    })
    auth.user = data
    router.push({ name: 'home' })
  } catch (e) {
    error.value = e.response?.data?.message || '수정 중 오류가 발생했습니다'
  } finally {
    loading.value = false
  }
}

// 비밀번호 변경
async function PasswordUpdate() {
  if (loading.value) return
  loading.value = true
  error.value   = ''
  try {
    await axios.post('http://127.0.0.1:8000/accounts/password/change/', {
      new_password1: passwordNew.value,
      new_password2: passwordConfirm.value,
    })
    router.push({ name: 'home' })
  } catch (e) {
    error.value = e.response?.data?.message || '비밀번호 변경 중 오류가 발생했습니다'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 추가 커스텀 스타일 필요 시 여기에 작성하세요 */
</style>
