<template>
  <div class="post-form">
    <!-- 제목 입력 -->
    <TitleInput v-model="title" placeholder="게시글 제목" />
    <!-- 작성자 입력 -->
    <AuthorInput v-model="author" placeholder="게시글 작성자" />

    <!-- 내용 에디터 -->
    <label class="content-label">내용</label>
    <div ref="editorRef" class="toastui-editor"></div>

    <!-- 버튼 그룹 -->
    <div class="buttons">
      <button @click="onSubmit">저장</button>
      <button @click="onCancel">취소</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import TitleInput from '@/components/TitleInput.vue'
import { defineEmits } from 'vue'
import AuthorInput from './AuthorInput.vue'

const emits = defineEmits(['submit','cancel'])

const title = ref('')
const author = ref('')
let content = ''

const editorRef = ref(null)
let editorInstance = null

onMounted(() => {
  editorInstance = new toastui.Editor({
    el: editorRef.value,
    initialEditType: 'wysiwyg',
    previewStyle: 'vertical',
    height: '300px',
    initialValue: content
  })
})

onBeforeUnmount(() => {
  if (editorInstance) editorInstance.destroy()
})

function onSubmit() {
  content = editorInstance.getMarkdown()
  emits('submit', { title: title.value, author: author.value, content })
}

function onCancel() {
  emits('cancel')
}
</script>

<style scoped>
.post-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-label {
  font-weight: bold;
  margin-bottom: 8px;
}

.toastui-editor {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px;
  min-height: 300px;
  margin-bottom: 16px;
}

.buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.buttons button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>