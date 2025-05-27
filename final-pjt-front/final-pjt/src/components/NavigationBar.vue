<template>
  <v-app-bar app color="white" light class="nav-bar">
    <!-- 좌측 네비게이션 -->
    <v-toolbar-items>
      <v-btn text :to="{ name: 'home' }">
        <img :src="route.name === 'home'
          ? '/images/cocktail.png'
          : '/images/emptyglass.png'" alt="Home" class="nav-icon" />
        Home
      </v-btn>
      <v-btn text :to="{ name: 'productList' }">
        <img :src="route.name === 'productList'
          ? '/images/cocktail.png'
          : '/images/emptyglass.png'" alt="예적금상품" class="nav-icon" />
        예·적금상품
      </v-btn>
      <v-btn text :to="{ name: 'spotPrice' }">
        <img :src="route.name === 'spotPrice'
          ? '/images/cocktail.png'
          : '/images/emptyglass.png'" alt="현물상품" class="nav-icon" />
        현물상품
      </v-btn>
      <v-btn text :to="{ name: 'videoStock' }">
        <img :src="route.name === 'videoStock'
          ? '/images/cocktail.png'
          : '/images/emptyglass.png'" alt="주식정보검색" class="nav-icon" />
        주식정보검색
      </v-btn>
      <v-btn text :to="{ name: 'bankMap' }">
        <img :src="route.name === 'bankMap'
          ? '/images/cocktail.png'
          : '/images/emptyglass.png'" alt="은행지도" class="nav-icon" />
        은행지도
      </v-btn>
      <v-btn text :to="{ name: 'articles' }">
        <img :src="route.name === 'articles'
          ? '/images/cocktail.png'
          : '/images/emptyglass.png'" alt="커뮤니티" class="nav-icon" />
        커뮤니티
      </v-btn>
      <!-- 추천상품 (투자 프로필 포함) -->
      <v-btn text @click="goToRecommendations">
        <img :src="['investmentProfile', 'recommendations', 'survey', 'investmentGoal'].includes(route.name) 
          ? '/images/cocktail.png' 
          : '/images/emptyglass.png'" 
          alt="추천상품" 
          class="nav-icon" 
        />
        추천상품
      </v-btn>
    </v-toolbar-items>

    <v-spacer />

    <!-- 우측 네비게이션: 로그인 상태에 따라 변경 -->
    <v-toolbar-items>
      <template v-if="isAuth">
        <v-btn text @click="logout">
          <img src="/images/wineglass.png" alt="로그아웃" class="nav-icon" />
          로그아웃
        </v-btn>
        <v-btn text :to="{ name: 'profile' }">
          <img :src="route.name === 'profile'
            ? '/images/cocktail2.png'
            : '/images/emptyglass.png'" alt="회원정보수정" class="nav-icon" />
          회원정보수정
        </v-btn>
      </template>
      <template v-else>
        <v-btn text :to="{ name: 'signup' }">
          <img :src="route.name === 'signup'
            ? '/images/cocktail2.png'
            : '/images/emptyglass.png'" alt="회원가입" class="nav-icon" />
          회원가입
        </v-btn>
        <v-btn text :to="{ name: 'login' }">
          <img :src="route.name === 'login'
            ? '/images/cocktail2.png'
            : '/images/emptyglass.png'" alt="로그인" class="nav-icon" />
          로그인
        </v-btn>
      </template>
    </v-toolbar-items>
  </v-app-bar>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { investmentAPI } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const route = useRoute()
const isAuth = computed(() => authStore.isAuthenticated)

async function goToRecommendations() {
  if (!isAuth.value) {
    router.push({ name: 'login' })
    return
  }

  try {
    const { data } = await investmentAPI.checkStatus()
    if (!data.has_investment_profile || !data.has_investment_goal) {
      router.push({ name: 'investmentProfile' })
    } else {
      router.push({ name: 'recommendations' })
    }
  } catch (error) {
    console.error('프로필 상태 확인 실패:', error)
    router.push({ name: 'investmentProfile' })
  }
}

function logout() {
  authStore.logout()
  router.push({ name: 'home' })
}
</script>

<style scoped>
.nav-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
}

/* 네비게이션 바 하단에 검은색 경계선 추가 */
.nav-bar {
  border-bottom: 1px solid #000;
}
</style>
