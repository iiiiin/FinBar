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

<template>
  <v-app-bar app color="white" light class="nav-bar">
    <!-- 햄버거 아이콘: 화면이 작을 때만 -->
    <v-app-bar-nav-icon class="hidden-md-and-up" @click="drawer = !drawer" />

    <!-- 데스크탑용 네비게이션 메뉴 -->
    <v-toolbar-items class="hidden-sm-and-down">
      <v-btn
        v-for="item in navItems"
        :key="item.name"
        text
        :to="item.route"
        link
      >
        <img
          :src="route.name === item.name ? item.activeIcon : item.icon"
          alt=""
          class="nav-icon"
        />
        {{ item.title }}
      </v-btn>
    </v-toolbar-items>

    <v-spacer />

    <!-- 우측 인증 버튼 (데스크탑) -->
    <v-toolbar-items class="hidden-sm-and-down">
      <template v-if="isAuth">
        <v-btn text @click="logout">  
          <img src="/images/wineglass.png" class="nav-icon" alt="로그아웃" />
          로그아웃
        </v-btn>
        <v-btn text :to="{ name: 'profile' }" link>  
          <img
            :src="route.name === 'profile'
              ? '/images/cocktail2.png'
              : '/images/emptyglass.png'"
            class="nav-icon"
            alt="회원정보수정"
          />
          회원정보수정
        </v-btn>
      </template>
      <template v-else>
        <v-btn text :to="{ name: 'signup' }" link>
          <img
            :src="route.name === 'signup'
              ? '/images/cocktail2.png'
              : '/images/emptyglass.png'"
            class="nav-icon"
            alt="회원가입"
          />
          회원가입
        </v-btn>
        <v-btn text :to="{ name: 'login' }" link>
          <img
            :src="route.name === 'login'
              ? '/images/cocktail2.png'
              : '/images/emptyglass.png'"
            class="nav-icon"
            alt="로그인"
          />
          로그인
        </v-btn>
      </template>
    </v-toolbar-items>
  </v-app-bar>

  <!-- 모바일용 네비게이션 드로어 -->
  <v-navigation-drawer
    v-model="drawer"
    app
    temporary
    class="mobile-drawer"
  >
    <v-list nav dense>
      <v-list-item
        v-for="item in navItems"
        :key="item.name"
        :to="item.route"
        link
        @click="drawer = false"
      >
        <template #prepend>
          <img
            :src="route.name === item.name ? item.activeIcon : item.icon"
            class="nav-icon"
            alt=""
          />
        </template>
        <v-list-item-title>{{ item.title }}</v-list-item-title>
      </v-list-item>

      <v-divider class="my-2" />

      <template v-if="isAuth">
        <v-list-item link @click="logout">
          <template #prepend>
            <img src="/images/wineglass.png" class="nav-icon" alt="로그아웃" />
          </template>
          <v-list-item-title>로그아웃</v-list-item-title>
        </v-list-item>

        <v-list-item
          link
          :to="{ name: 'profile' }"
          @click="drawer = false"
        >
          <template #prepend>
            <img
              :src="route.name === 'profile'
                ? '/images/cocktail2.png'
                : '/images/emptyglass.png'"
              class="nav-icon"
              alt="회원정보수정"
            />
          </template>
          <v-list-item-title>회원정보수정</v-list-item-title>
        </v-list-item>
      </template>

      <template v-else>
        <v-list-item
          link
          :to="{ name: 'signup' }"
          @click="drawer = false"
        >
          <template #prepend>
            <img
              :src="route.name === 'signup'
                ? '/images/cocktail2.png'
                : '/images/emptyglass.png'"
              class="nav-icon"
              alt="회원가입"
            />
          </template>
          <v-list-item-title>회원가입</v-list-item-title>
        </v-list-item>

        <v-list-item
          link
          :to="{ name: 'login' }"
          @click="drawer = false"
        >
          <template #prepend>
            <img
              :src="route.name === 'login'
                ? '/images/cocktail2.png'
                : '/images/emptyglass.png'"
              class="nav-icon"
              alt="로그인"
            />
          </template>
          <v-list-item-title>로그인</v-list-item-title>
        </v-list-item>
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router    = useRouter()
const route     = useRoute()
const authStore = useAuthStore()
const isAuth    = computed(() => authStore.isLoggedIn)
const drawer    = ref(false)

const navItems = [
  { name: 'home',        title: 'Home',      route: { name: 'home' },        icon: '/images/emptyglass.png', activeIcon: '/images/cocktail.png' },
  { name: 'productList', title: '예·적금상품', route: { name: 'productList' }, icon: '/images/emptyglass.png', activeIcon: '/images/cocktail.png' },
  { name: 'spotPrice',   title: '현물상품',   route: { name: 'spotPrice' },   icon: '/images/emptyglass.png', activeIcon: '/images/cocktail.png' },
  { name: 'videoStock',  title: '주식정보검색', route: { name: 'videoStock' },  icon: '/images/emptyglass.png', activeIcon: '/images/cocktail.png' },
  { name: 'bankMap',     title: '은행지도',   route: { name: 'bankMap' },     icon: '/images/emptyglass.png', activeIcon: '/images/cocktail.png' },
  { name: 'articles',    title: '커뮤니티',   route: { name: 'articles' },    icon: '/images/emptyglass.png', activeIcon: '/images/cocktail.png' },
]

function logout() {
  authStore.logout()
  router.push({ name: 'home' })
  drawer.value = false
}
</script>

<style scoped>
.nav-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
}

.nav-bar {
  border-bottom: 1px solid #000;
}

.mobile-drawer .v-list-item {
  min-height: 48px;
}
</style>
