<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <!-- 네비게이션 바 -->
    <v-row><v-col cols="12"><NavigationBar/></v-col></v-row>

    <!-- 페이지 제목 -->
    <v-row class="my-4"><v-col cols="12"><Title :title="pageTitle"/></v-col></v-row>

    <!-- 검색창 + 버튼 -->
    <v-row align="center" class="mb-4" no-gutters>
      <v-col cols="12" sm="9" md="10" class="pr-2">
        <SearchBar v-model="q" @search="fetchArticles"/>
      </v-col>
      <v-col cols="12" sm="3" md="2">
        <v-btn block color="primary" @click="fetchArticles">검색</v-btn>
      </v-col>
    </v-row>

    <!-- 로딩 스피너 -->
    <v-row justify="center" v-if="isLoading" class="my-6">
      <v-col cols="auto">
        <LoadingSpinner
        :images="loadingImages"
        :interval="200"
        />
      </v-col>
    </v-row>

    <!-- 결과 카드 -->
    <v-row v-else-if="videos.length" dense>
      <v-col
        v-for="video in videos"
        :key="video.id.videoId"
        cols="12" sm="6" md="4"
      >
        <v-card
          class="mb-4" hover style="cursor:pointer"
          @click="goToDetail(video.id.videoId)"
        >
          <v-img
            :src="video.snippet.thumbnails.medium.url"
            height="140px" cover
          />
          <v-card-text>
            <div class="video-title" v-html="video.snippet.title"></div>
            <div class="video-date">{{ formatDate(video.snippet.publishedAt) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

      <!-- 인증 에러 메시지 -->
    <v-row v-else-if="errorMessage" class="text-center">
      <v-col cols="12">
        <v-alert type="error" color="grey darken-2" class="white--text">
          {{ errorMessage }}
        </v-alert>
      </v-col>
    </v-row>

    <!-- 결과 없음 -->
    <v-row v-else class="text-center">
      <v-col cols="12"><p>검색 결과가 없습니다.</p></v-col>
    </v-row>
    <PlaceFooter src="/images/plate.png" alt="메뉴접시" />
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/NavigationBar.vue'
import SearchBar     from '@/components/SearchBar.vue'
import Title         from '@/components/Title.vue'
import PlaceFooter from '@/components/PlaceFooter.vue'
import { useVideoStore } from '@/stores/videoStore'
import apiClient from '@/services/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const pageTitle = '관심 종목 정보 검색'
const q         = ref('')
const isLoading = ref(false)
const router    = useRouter()
const errorMessage = ref('')

const store  = useVideoStore()
const videos = store.videos   // Ref<Array>
const loadingImages = [
  '/images/shaker1.png',
  '/images/shaker2.png',
]

function goToDetail(id) {
  router.push({ name: 'videoDetail', params: { id } })
}

async function fetchArticles() {
  if (!q.value) return
  // 1) 기존 데이터 지우기
  videos.splice(0, videos.length)
  errorMessage.value = ''
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const { data } = await apiClient.get('/youtube/', {
      params: { q: q.value },
      headers: { Authorization: `Token ${token}` }
    })
    // 2) 새 데이터 삽입
    videos.splice(0, 0, ...data.items)
    store.lastQuery = q.value
  } catch (err) {
    if (err.response && err.response.status === 401) {
      // 401일 때만 에러 메시지 표시
      errorMessage.value = '인증 오류가 발생했습니다. 다시 로그인해주세요.'
    } else {
      console.error('API 호출 실패', err)
      errorMessage.value = '검색 결과를 불러오는 중 오류가 발생했습니다.'
    }
  } finally {
    isLoading.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric'
  })
}

onMounted(() => {
  if (store.lastQuery) {
    q.value = store.lastQuery
    fetchArticles()
  }
})
</script>

<style scoped>
.v-card { cursor: pointer; }
.video-title {
  font-size: 16px; font-weight: 600; line-height: 1.4;
  margin-bottom: 4px; word-break: break-word;
}
.video-date { font-size: 14px; color: #666; }
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
