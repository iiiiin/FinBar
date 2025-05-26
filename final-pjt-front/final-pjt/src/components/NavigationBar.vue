<template>
  <v-app-bar app color="primary" dark>
    <!-- 좌측 네비게이션 -->
    <v-toolbar-items>
      <v-btn text :to="{name: 'home'}">Home</v-btn>
      <v-btn text :to="{name: 'productList'}">예적금상품</v-btn>
      <v-btn text :to="{name: 'spotPrice'}">현물상품</v-btn>
      <v-btn text :to="{name: 'videoStock'}">주식정보검색</v-btn>
      <v-btn text :to="{name: 'bankMap'}">은행지도</v-btn>
      <v-btn text :to="{name: 'articles'}">커뮤니티</v-btn>
    </v-toolbar-items>

    <v-spacer />

    <!-- 우측 네비게이션: 로그인 상태에 따라 변경 -->
    <v-toolbar-items>
      <template v-if="isAuth">
        <v-btn text @click="logout">로그아웃</v-btn>
        <v-btn text :to="{name: 'profile'}">회원정보수정</v-btn>
      </template>
      <template v-else>
        <v-btn text :to="{name: 'signup'}">회원가입</v-btn>
        <v-btn text :to="{name: 'login'}">로그인</v-btn>
      </template>
    </v-toolbar-items>
  </v-app-bar>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router    = useRouter()
const authStore = useAuthStore()
const isAuth    = computed(() => authStore.isLoggedIn)

function logout() {
  authStore.logout()
  router.push({ name: 'home' })
}
</script>

<style scoped>
/* 필요시 추가 스타일 작성 */
</style>
