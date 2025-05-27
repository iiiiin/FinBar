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


    <!-- 글 작성 버튼 -->
    <v-row v-if="isAuth">
      <v-col cols="12" class="text-right mb-4">
        <v-btn color="primary" @click="goCreate">글 작성</v-btn>
      </v-col>
    </v-row>


    <!-- 게시글 리스트 -->
    <v-row>
      <v-col cols="12" v-if="!articles.length">
        <v-alert type="info" border="start" colored-border>
          등록된 게시글이 없습니다.
        </v-alert>
      </v-col>
      <v-col cols="12" v-else>
        <PostList :posts="articles" @select="goDetail" />
      </v-col>
    </v-row>

    <!-- 페이지네이션 -->
    <v-row justify="center" class="mt-4">
      <Pagination :page="page" :total="totalPages" @change="onPageChange" />
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore }  from '@/stores/auth'
import apiClient from '@/services/api'
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import SearchBar     from '@/components/SearchBar.vue'
import PostList      from '@/components/PostList.vue'
import Pagination    from '@/components/Pagination.vue'
import Title         from '@/components/Title.vue'

const pageTitle  = '게시글 목록'
const router     = useRouter()
const q          = ref('')
const articles   = ref([])
const page       = ref(1)
const totalPages = ref(1)
const auth = useAuthStore()
const isAuth     = computed(() => auth.isLoggedIn)

// 게시글 목록 조회
async function fetchArticles() {
  try {
    const { data } = await apiClient.get('/articles/', {
    })
    articles.value = data
  } catch (error) {
    console.error(error)
  }
}

// 상세 페이지로 이동
function goDetail(post) {
  console.log(post.id)
  router.push({ name: 'articleDetail', params: { id: post.id }})
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
/* v-alert 전체 스타일 오버라이드 */
::v-deep .v-alert {
  background-color: #ffffff !important;       /* 흰 배경 */
  color: #000000 !important;                  /* 검은 글씨 */
  box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important; /* 연한 회색 그림자 */
  border: none !important;                    /* 테두리 제거 */
}

/* colored-border, border-start 등으로 들어온 좌측 컬러바도 제거 */
::v-deep .v-alert--border-start {
  border-left: none !important;
}

/* 만약 다른 border 속성이 붙는 경우에도 완전 제거 */
::v-deep .v-alert {
  border-width: 0 !important;
}
</style>
