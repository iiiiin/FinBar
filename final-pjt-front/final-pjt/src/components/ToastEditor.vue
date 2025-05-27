<template>
  <div ref="editorRef" class="toastui-editor"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, defineProps, defineEmits, watch } from 'vue'

const props = defineProps({
  content: { type: String, default: '' }
})
const emits = defineEmits(['update:content'])

const editorRef = ref(null)
let editorInstance = null

onMounted(() => {
  editorInstance = new toastui.Editor({
    el: editorRef.value,
    initialEditType: 'wysiwyg',
    previewStyle: 'vertical',
    height: '400px',
    initialValue: props.content
  })
  editorInstance.on('change', () => {
    emits('update:content', editorInstance.getMarkdown())
  })
})

// **prop 변경 감지 후 에디터 내용 업데이트**
watch(
  () => props.content,
  (newContent) => {
    if (editorInstance && newContent !== editorInstance.getMarkdown()) {
      // Markdown 으로 쓰고 있다면 setMarkdown
      editorInstance.setMarkdown(newContent)
      // HTML 로 쓰고 싶다면: editorInstance.setHTML(newContent)
    }
  }
)

onBeforeUnmount(() => {
  if (editorInstance) {
    editorInstance.destroy()
  }
})
</script>


<style scoped>
.toastui-editor {
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>