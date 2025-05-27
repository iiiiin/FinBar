<template>
  <v-container class="mx-auto" style="max-width:800px;">
    <v-row>
      <v-col cols="12">
        <NavigationBar />
      </v-col>
    </v-row>
    <v-row class="my-4">
      <v-col cols="12">
        <Title title="게시글 수정" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-form @submit.prevent="onUpdate">
          <TitleInput v-model="form.title" />
          <ToastEditor v-model:content="form.content" />
          <v-row class="mt-4">
            <v-col cols="6">
              <v-btn block outlined color="secondary" @click="goBack">취소</v-btn>
            </v-col>
            <v-col cols="6">
              <v-btn block color="primary" type="submit">저장</v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title from '@/components/Title.vue'
import TitleInput from '@/components/TitleInput.vue'
import ToastEditor from '@/components/ToastEditor.vue'

const router = useRouter()
const route = useRoute()
const form = ref({ title: '', content: '' })

// 초기 데이터 로드
onMounted(async () => {
  const id = route.params.id
  try {
    const { data } = await axios.get(`http://127.0.0.1:8000/articles/${id}/`)
    form.value.title   = data.title
    form.value.content = data.content  // Markdown or HTML
  } catch (e) {
    console.error(e)
  }
})

// 수정 요청
async function onUpdate() {
  const id = route.params.id
  try {
    await axios.put(`http://127.0.0.1:8000/articles/${id}/`, {
      title:   form.value.title,
      content: form.value.content
    })
    router.push({ name: 'articleDetail', params: { id } })
  } catch (e) {
    console.error(e)
    alert('수정에 실패했습니다.')
  }
}

function goBack() {
  router.back()
}
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
</style>
