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
            작성자: {{ article.nickname }} • {{ formatDate(article.created_at) }}
          </v-card-subtitle>
          <v-divider />
          <v-card-text>
            <div v-html="article.content"></div>
          </v-card-text>
          <v-card-actions>
            <v-btn text @click="goBack">뒤로</v-btn>
            <v-spacer />
            <template v-if="isOwner">
              <v-btn text color="error" @click="deleteArticle">삭제</v-btn>
              <v-btn text color="primary" @click="goEdit">수정</v-btn>
            </template>
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
              <template v-for="comment in comments" :key="comment.id">
                <v-list-item class="comment-item">
                    <!-- 댓글 내용 or inline edit -->
                    <template v-if="editingId !== comment.id">
                      <div>
                        <div class="font-weight-medium">{{ comment.nickname }}</div>
                        <div>{{ comment.content }}</div>
                        <div class="text-caption grey--text">{{ formatDate(comment.created_at) }}</div>
                      </div>
                    </template>
                    <template v-else>
                      <v-text-field
                        v-model="editContent"
                        dense
                        outlined
                        class="flex-grow-1 mr-2"
                      />
                    </template>

                  <!-- 액션 버튼, 같은 행 우측 배치 -->
                  <v-list-item-action class="d-flex align-center">
                    <template v-if="editingId !== comment.id && auth.username === comment.username">
                      <v-btn small text color="primary" @click="startEdit(comment)">수정</v-btn>
                      <v-btn small text color="error" @click="deleteComment(comment.id)">삭제</v-btn>
                    </template>
                    <template v-else-if="editingId === comment.id">
                      <v-btn small text color="secondary" @click="cancelEdit">취소</v-btn>
                      <v-btn small text color="primary" @click="saveEdit(comment.id)">저장</v-btn>
                    </template>
                  </v-list-item-action>
                </v-list-item>
                <v-divider inset />
              </template>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title from '@/components/Title.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const pageTitle = '게시글 상세'

const article = ref({ title: '', content: '', created_at: '', username: '' })
const comments = ref([])
const newComment = ref('')

// inline edit state
const editingId = ref(null)
const editContent = ref('')

// 로그인 여부 체크
if (!auth.isLoggedIn) {
  router.replace({ name: 'login' })
}

// 글 소유자 여부
const isOwner = computed(() => auth.username === article.value.username)

// 날짜 포맷
function formatDate(dateStr) {
  return dateStr ? new Date(dateStr).toLocaleString() : ''
}

// 댓글 목록 로드
async function loadComments() {
  try {
    const { data: cmts } = await axios.get(`http://127.0.0.1:8000/articles/${route.params.id}/comment/`)
    comments.value = cmts
  } catch (e) {
    if (e.response?.status === 404) comments.value = []
    else console.error(e)
  }
}

// 게시글 로드 및 댓글 로드
async function loadData() {
  try {
    const { data: art } = await axios.get(`http://127.0.0.1:8000/articles/${route.params.id}/`)
    article.value = art
  } catch (e) {
    console.error(e)
  }
  await loadComments()
}

onMounted(loadData)

// 댓글 작성
async function addComment() {
  if (!newComment.value.trim()) return
  try {
    await axios.post(`http://127.0.0.1:8000/articles/${route.params.id}/comment/`, { content: newComment.value })
    newComment.value = ''
    await loadComments()
  } catch (e) {
    console.error(e)
    alert('댓글 작성에 실패했습니다.')
  }
}

// 댓글 삭제
async function deleteComment(id) {
  try {
    await axios.delete(`http://127.0.0.1:8000/articles/${route.params.id}/comment/${id}/`)
    await loadComments()
  } catch (e) {
    console.error(e)
    alert('댓글 삭제에 실패했습니다.')
  }
}

// 댓글 수정 시작
function startEdit(comment) {
  editingId.value = comment.id
  editContent.value = comment.content
}
// 댓글 수정 취소
function cancelEdit() {
  editingId.value = null
  editContent.value = ''
}
// 댓글 수정 저장
async function saveEdit(id) {
  if (!editContent.value.trim()) return
  try {
    await axios.put(
      `http://127.0.0.1:8000/articles/${route.params.id}/comment/${id}/`,
      { article_pk: route.params.id,
        comment_pk: id,
        content: editContent.value }
    )
    cancelEdit()
    await loadComments()
  } catch (e) {
    console.error(e)
    alert('댓글 수정에 실패했습니다.')
  }
}

// 뒤로가기
function goBack() {
  router.back()
}
// 게시글 수정
function goEdit() {
  if (!isOwner.value) return
  router.push({ name: 'articleUpdate', params: { id: route.params.id } })
}
// 게시글 삭제
async function deleteArticle() {
  if (!isOwner.value) return
  if (!confirm('정말 삭제하시겠습니까?')) return
  try {
    await axios.delete(`http://127.0.0.1:8000/articles/${route.params.id}/`)
    router.push({ name: 'articles' })
  } catch (e) {
    console.error(e)
    alert('삭제에 실패했습니다.')
  }
}
</script>

<style scoped>
.text-center { text-align: center; }
.comment-item { align-items: center; }
</style>
