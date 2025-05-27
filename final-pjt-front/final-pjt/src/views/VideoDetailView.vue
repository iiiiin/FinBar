<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <!-- 돌아가기 버튼 -->
    <v-row class="my-4">
      <v-col cols="12">
        <v-btn text @click="goBack">← 돌아가기</v-btn>
      </v-col>
    </v-row>

    <!-- 로딩 상태 -->
    <v-row justify="center" v-if="isLoading">
      <v-col cols="auto">
        <LoadingSpinner :images="loadingImages" :interval="200" />
      </v-col>
    </v-row>

    <!-- 에러 메시지 -->
    <v-row v-if="errorMessage" class="text-center">
      <v-col cols="12">
        <v-alert type="error" color="grey darken-2" class="white--text">
          {{ errorMessage }}
        </v-alert>
      </v-col>
    </v-row>

    <!-- 동영상 + 메타 -->
    <v-row v-if="!isLoading && !errorMessage">
      <v-col cols="12">
        <div class="video-wrapper">
          <iframe
            :src="`https://www.youtube.com/embed/${videoId}`"
            frameborder="0"
            allowfullscreen
            width="100%"
            height="400"
          ></iframe>
        </div>
      </v-col>
      <v-col cols="12" class="mt-4">
        <h2 class="text-h6 mb-2">{{ title }}</h2>
        <div class="video-description" v-html="formattedDescription"></div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/services/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const videoId = route.params.id

// UI 상태
const title = ref('')
const description = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const loadingImages = [
  '/images/shaker1.png',
  '/images/shaker2.png',
]

// YouTube description 안에 줄바꿈 문자를 <br> 태그로 바꿔서 렌더링
const formattedDescription = computed(() =>
  description.value
    .split('\n')
    .map(line => `<p>${line}</p>`)
    .join('')
)

async function fetchVideoDetail() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const token = localStorage.getItem('token')
    const { data } = await apiClient.get(
      `/youtube/${videoId}/`,
      { headers: { Authorization: `Token ${token}` } }
    )
    title.value = data.title
    description.value = data.description
  } catch (err) {
    console.error(err)
    errorMessage.value = '비디오 정보를 불러오는 중 오류가 발생했습니다.'
  } finally {
    isLoading.value = false
  }
}

function goBack() {
  router.back()
}

onMounted(() => {
  fetchVideoDetail()
})
</script>

<style scoped>
.video-wrapper {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 비율 유지 */
  height: 0;
  overflow: hidden;
}
.video-wrapper iframe {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
}
.video-description p {
  margin-bottom: 1em;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
