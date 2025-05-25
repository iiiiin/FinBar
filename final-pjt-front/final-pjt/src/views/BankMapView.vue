<template>
    <v-container class="mx-auto" :style="{ maxWidth : '800px'}">
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
          <v-btn block color="primary" @click="fetchArticles">
            검색
          </v-btn>
        </v-col>
      </v-row>
    
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from 'axios'
  import NavigationBar from '@/components/NavigationBar.vue'
  import SearchBar     from '@/components/SearchBar.vue'
  import Title         from '@/components/Title.vue'
  
  const pageTitle  = '관심 종목 정보 검색'
  const router     = useRouter()
  const q          = ref('')
  const articles   = ref([])
  const page       = ref(1)
  const totalPages = ref(1)
  
  // 게시글 목록 조회
  async function fetchArticles() {
    try {
      const { data } = await axios.get('http://127.0.0.1:8000/articles/', {
        // params: { search: q.value, page: page.value }
      })
      articles.value = data
      // totalPages.value = data.total_pages
    } catch (error) {
      console.error(error)
    }
  }
  
  // 상세 페이지로 이동
  function goDetail(post) {
    router.push({ name: 'articleDetail', params: { id : post.id }})
  }
  
  // 페이지 변경
  function onPageChange(newPage) {
    page.value = newPage
    fetchArticles()
  }
  
  // 글 작성 페이지로 이동
  function goCreate() {
    router.push({ name: 'articleCreate' })
  }
  
  onMounted(fetchArticles)
  </script>
  
  <style scoped>
  /* 필요 시 컨테이너 중앙 정렬 이외 추가 스타일 작성 */
  </style>
  