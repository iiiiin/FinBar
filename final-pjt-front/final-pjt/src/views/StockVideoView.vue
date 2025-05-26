<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <!-- 네비게이션 바 -->
    <v-row>
      <v-col cols="12">
        <NavigationBar />
      </v-col>
    </v-row>

    <!-- 페이지 제목 -->
    <v-row class="my-4">
      <v-col cols="12">
        <Title :title="pageTitle" />
      </v-col>
    </v-row>

    <!-- 검색창 + 검색 버튼 -->
    <v-row align="center" class="mb-4" no-gutters>
      <v-col cols="12" sm="9" md="10" class="pr-2">
        <SearchBar v-model="q" @search="fetchArticles" />
      </v-col>
      <v-col cols="12" sm="3" md="2">
        <v-btn block color="primary" @click="fetchArticles">검색</v-btn>
      </v-col>
    </v-row>

    <!-- 로딩 표시 -->
    <v-row justify="center" v-if="isLoading" class="my-6">
      <v-col cols="auto">
        <v-progress-circular indeterminate color="primary" size="40" />
      </v-col>
    </v-row>

    <!-- 유튜브 영상 결과 -->
    <v-row v-if="videos.value.length" dense>
      <v-col
        v-for="video in videos.value"
        :key="video.id.videoId"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card
          class="mb-4"
          hover
          style="cursor: pointer"
          @click="goToDetail(video.id.videoId)"
        >
          <v-img
            :src="video.snippet.thumbnails.medium.url"
            height="140px"
            cover
          ></v-img>
          <v-card-text>
            <div class="video-title">
              {{ video.snippet.title }}
            </div>
            <div class="video-date">
              {{ formatDate(video.snippet.publishedAt) }}
            </div>
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
import NavigationBar from '@/components/NavigationBar.vue'
import SearchBar from '@/components/SearchBar.vue'
import Title from '@/components/Title.vue'
import { useVideoStore } from '@/stores/videoStore'

const pageTitle = '관심 종목 정보 검색'
const q = ref('')
const isLoading = ref(false)
const router = useRouter()

const store = useVideoStore()
const videos = store.videos  // ref([])

function goToDetail(videoId) {
  router.push({ name: 'videoDetail', params: { id: videoId } })
}

async function fetchArticles() {
  if (!q.value) return
  videos.value.splice(0, videos.value.length)  // 기존 카드 제거
  isLoading.value = true

  try {
    const token = localStorage.getItem('token')
    const { data } = await axios.get('http://localhost:8000/youtube/', {
      params: { q: q.value },
      headers: {
        Authorization: `Token ${token}`
      }
    })
    videos.value.splice(0, 0, ...data.items) // 새 데이터 삽입
    store.lastQuery = q.value
  } catch (error) {
    console.error('백엔드 API 호출 실패:', error)
  } finally {
    isLoading.value = false
  }
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  if (store.lastQuery) {
    q.value = store.lastQuery
  }
})
</script>

<style scoped>
.v-card {
  cursor: pointer;
}
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
</style>
