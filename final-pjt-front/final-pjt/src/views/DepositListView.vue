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
  
    
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from 'axios'
  import NavigationBar from '@/components/NavigationBar.vue'
  import SearchBar     from '@/components/SearchBar.vue'
  import Title         from '@/components/Title.vue'
  
  const pageTitle  = '예금/적금 상품 목록'
  const router     = useRouter()
  const q          = ref('')
  const articles   = ref([])
  const page       = ref(1)
  const totalPages = ref(1)
  
  
  
  
  // onMounted(fetchArticles)
  </script>
  
  <style scoped>
  /* 필요 시 컨테이너 중앙 정렬 이외 추가 스타일 작성 */
  </style>
  