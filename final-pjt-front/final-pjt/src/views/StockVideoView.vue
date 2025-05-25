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
  
      <!-- 유튜브 영상 결과 -->
      <v-row v-if="videos.length" dense>
        <v-col
          v-for="video in videos"
          :key="video.id.videoId"
          cols="12"
          sm="6"
          md="4"
        >
          <a
            :href="`https://www.youtube.com/watch?v=${video.id.videoId}`"
            target="_blank"
            rel="noopener noreferrer"
            style="text-decoration: none;"
          >
            <v-card class="mb-4" hover>
              <v-img
                :src="video.snippet.thumbnails.medium.url"
                height="180px"
                cover
              ></v-img>
              <v-card-title class="text-subtitle-1">
                {{ video.snippet.title }}
              </v-card-title>
            </v-card>
          </a>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  
  <script setup>
  import { ref } from 'vue'
  import NavigationBar from '@/components/NavigationBar.vue'
  import SearchBar from '@/components/SearchBar.vue'
  import Title from '@/components/Title.vue'
  import axios from 'axios'
  
  const pageTitle = '관심 종목 정보 검색'
  const q = ref('')
  const videos = ref([])
  
  async function fetchArticles() {
    if (!q.value) return
    try {
      const { data } = await axios.get('http://localhost:8000/api/youtube/', {
        params: { q: q.value }
      })
      videos.value = data.items
    } catch (error) {
      console.error('백엔드 API 호출 실패:', error)
    }
  }
  </script>
  
  <style scoped>
  .v-card {
    cursor: pointer;
  }
  </style>