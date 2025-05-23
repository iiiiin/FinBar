<template>
  <v-container class="mx-auto" style="max-width:800px;">
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

    <!-- 게시글 상세 -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="headline">{{ article.title }}</v-card-title>
          <v-card-subtitle>
            작성자: {{ nickname }} • {{ formatDate(created_at) }}
          </v-card-subtitle>
          <v-divider />
          <v-card-text>
            <div v-html="article.content"></div>
          </v-card-text>
          <v-card-actions>
            <v-btn text @click="goBack">뒤로</v-btn>
            <v-spacer />
            <v-btn text color="error" @click="deleteArticle">삭제</v-btn>
            <v-btn text color="primary" @click="goEdit">수정</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- 댓글 섹션 -->
    <v-row class="mt-6">
      <v-col cols="12">
        <v-card elevation="1">
          <v-card-title class="subtitle-1">댓글 ({{ comments.length }})</v-card-title>
          <v-divider />
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="comment in comments"
                :key="comment.id"
              >
                <v-list-item-content>
                  <v-list-item-subtitle>{{ comment.nickname }} • {{ formatDate(comment.created_at) }}</v-list-item-subtitle>
                  <v-list-item-title>{{ comment.text }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <!-- 댓글 입력 -->
            <v-form @submit.prevent="addComment">
              <v-text-field
                v-model="newComment"
                label="댓글 입력"
                dense
                outlined
              />
              <v-btn color="primary" @click="addComment">댓글 작성</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title         from '@/components/Title.vue'
import { useAuthStore } from '@/stores/auth'

const router     = useRouter()
const route      = useRoute()
const pageTitle  = '게시글 상세'
const article    = ref({ title: '', content: '', created_at: '' })
const comments   = ref([])
const newComment = ref('')
const nickname = route.query.nickname
const created_at = route.query.datetime
const auth = useAuthStore()

 // 로그인 여부 체크 (미인증 접근 차단)
//  if (!auth.isLoggedIn) {
//    router.replace({ name: 'login' })
//  }

 // 글 작성자와 현재 유저가 일치하는지
//  const isOwner = computed(() => {
//    // backend가 username 또는 nickname 필드를 준다고 가정
//    return auth.user?.username === article.value.author
//  })

// 날짜 포맷 함수
function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

// 데이터 로드
async function loadData() {
  const id = route.params.id
  try {
    const { data: art } = await axios.get(`http://127.0.0.1:8000/articles/${id}/`)
    article.value = art
    console.log(art)
    const { data: cmts } = await axios.get(`http://127.0.0.1:8000/articles/${id}/comments/`)
    comments.value = cmts
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadData)

// 뒤로가기
function goBack() {
  router.back()
}
// 수정 페이지로 이동
function goEdit() {
  router.push({ name: 'articleUpdate', params: { id: route.params.id } })
}
// 삭제
async function deleteArticle() {
  if (!confirm('정말 삭제하시겠습니까?')) return
  try {
    await axios.delete(`http://127.0.0.1:8000/articles/${route.params.id}/`)
    router.push({ name: 'articles' })
  } catch (e) {
    console.error(e)
    alert('삭제에 실패했습니다.')
  }
}
// 댓글 추가
async function addComment() {
  const id = route.params.id
  if (!newComment.value.trim()) return
  try {
    await axios.post(`http://127.0.0.1:8000/articles/${id}/comments/`, { text: newComment.value })
    newComment.value = ''
    // 댓글 다시 불러오기
    const { data: cmts } = await axios.get(`http://127.0.0.1:8000/articles/${id}/comments/`)
    comments.value = cmts
  } catch (e) {
    console.error(e)
    alert('댓글 작성에 실패했습니다.')
  }
}
</script>

<style scoped>
/* 필요 시 추가 스타일 */
</style>
