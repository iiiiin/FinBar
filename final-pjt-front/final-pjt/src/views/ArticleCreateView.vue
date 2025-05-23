<template>
  <v-container fluid>
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

    <!-- 글 작성 폼 -->
    <v-row>
      <v-col cols="12">
        <PostForm
          @submit="createPost"
          @cancel="goBack"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title         from '@/components/Title.vue'
import PostForm      from '@/components/PostForm.vue'

const router = useRouter()
const pageTitle = '새 글 작성'

// 게시글 생성 API 호출 후 목록 페이지로 이동
async function createPost(formData) {
  try {
    await axios.post('http://127.0.0.1:8000/articles/', formData)
    router.push({ name: 'articles' })
  } catch (error) {
    console.error(error)
    alert('게시글 생성에 실패했습니다.')
  }
}

// 취소 클릭 시 이전 페이지로 돌아가기
function goBack() {
  router.back()
}
</script>

<style scoped>
.v-container {
  max-width: 800px;
}
</style>