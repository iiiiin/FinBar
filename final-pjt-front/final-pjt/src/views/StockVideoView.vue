<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <!-- 네비게이션 바 -->
    <v-row><v-col cols="12"><NavigationBar ref="navBarRef"/></v-col></v-row>

    <!-- 페이지 제목 -->
    <v-row class="my-4"><v-col cols="12"><Title ref="titleRef" :title="pageTitle"/></v-col></v-row>

    <!-- 검색창 + 버튼 -->
    <v-row align="center" class="mb-4" no-gutters>
      <v-col cols="12" sm="9" md="10" class="pr-2">
        <SearchBar ref="searchBarRef" v-model="q" @search="fetchArticles"/>
      </v-col>
      <v-col cols="12" sm="3" md="2">
        <v-btn block color="primary" @click="fetchArticles">검색</v-btn>
      </v-col>
    </v-row>

    <!-- 로딩 스피너 -->
    <v-row justify="center" v-if="isLoading" class="my-6">
      <v-col cols="auto">
        <v-progress-circular indeterminate color="primary" size="40"/>
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
            <div class="video-title">{{ video.snippet.title }}</div>
            <div class="video-date">{{ formatDate(video.snippet.publishedAt) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 결과 없음 -->
    <v-row v-else class="text-center">
      <v-col cols="12"><p>검색 결과가 없습니다.</p></v-col>
    </v-row>
    <PlaceFooter ref="footerRef" src="/images/plate.png" alt="메뉴접시" />
  </v-container>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title from '@/components/Title.vue'
import SearchBar from '@/components/SearchBar.vue'
import PlaceFooter from '@/components/PlaceFooter.vue'
import { useVideoStore } from '@/stores/videoStore'

const router = useRouter()
const pageTitle = '관심 종목 정보 검색'

// 컴포넌트 참조
const navBarRef = ref(null)
const titleRef = ref(null)
const searchBarRef = ref(null)
const footerRef = ref(null)

// 상태 관리
const q = ref('')
const videos = ref([])
const isLoading = ref(false)

const store = useVideoStore()

function goToDetail(id) {
  if (!id) return
  router.push({ name: 'videoDetail', params: { id } })
}

async function fetchArticles() {
  if (!q.value?.trim()) return
  
  isLoading.value = true
  videos.value = [] // 배열 초기화
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('인증 토큰이 없습니다.')
    }

    const { data } = await axios.get('http://localhost:8000/youtube/', {
      params: { q: q.value },
      headers: { Authorization: `Token ${token}` }
    })

    if (!data?.items) {
      throw new Error('응답 데이터가 올바르지 않습니다.')
    }

    // 새 데이터 할당
    videos.value = data.items
    store.lastQuery = q.value
  } catch (err) {
    console.error('API 호출 실패:', err)
    videos.value = [] // 에러 시 배열 초기화
  } finally {
    isLoading.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  if (store.lastQuery) {
    q.value = store.lastQuery
    fetchArticles()
  }
})

// 컴포넌트 언마운트 전 정리 작업
onBeforeUnmount(() => {
  // 참조 정리
  if (navBarRef.value) navBarRef.value = null
  if (titleRef.value) titleRef.value = null
  if (searchBarRef.value) searchBarRef.value = null
  if (footerRef.value) footerRef.value = null
  
  // 상태 초기화
  q.value = ''
  videos.value = []
  isLoading.value = false
})
</script>

<style scoped>
.v-card { cursor: pointer; }
.video-title {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 4px;
  word-break: break-word;
}
.video-date { 
  font-size: 14px;
  color: #666;
}

/* Vuetify v-btn 기본 스타일 오버라이드 */
::v-deep .v-btn {
  background-color: #ffffff !important;
  color: #000000 !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
  border: none !important;
}

::v-deep .v-btn:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

::v-deep .v-btn--text {
  background-color: transparent !important;
  box-shadow: none !important;
  color: #000000 !important;
}
</style>
