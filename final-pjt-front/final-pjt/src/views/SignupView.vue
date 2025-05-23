<!-- src/views/Signup.vue -->
<template>
  <NavigationBar />
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
                :rules="[v => v.length >= 6 || '비밀번호는 6자 이상이어야 합니다']"
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
              <v-text-field
                v-model="nickname"
                label="닉네임"
                :rules="[v => !!v || '닉네임을 입력해주세요']"
                required
              />
              <v-text-field
                v-model="age"
                label="나이"
                type="number"
                :rules="[
                  v => !!v || '나이를 입력해주세요',
                  v => (v && v > 0) || '유효한 나이를 입력해주세요'
                ]"
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
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'

const router = useRouter()

const username  = ref('')
const password1 = ref('')
const password2 = ref('')
const email     = ref('')
const nickname  = ref('')
const age       = ref('')

const isSubmitting = ref(false)
const error = ref('')

async function handleSignup() {
  if (isSubmitting.value) return
  isSubmitting.value = true
  error.value = ''

  try {
    const res = await axios.post('http://127.0.0.1:8000/accounts/signup/', {
      username:  username.value,
      password1: password1.value,
      password2: password2.value,
      email:     email.value,
      nickname:  nickname.value,
      age:       age.value
    })
    console.log('signup success:', res.data)
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
.signup-page { }
</style>
