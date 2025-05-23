<template>
  <div ref="editorRef" class="toastui-editor"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, defineProps, defineEmits } from 'vue'

const props = defineProps({
  initialContent: { type: String, default: '' }
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
    initialValue: props.initialContent
  })
  // 내용 변경 시 emit
  editorInstance.on('change', () => {
    emits('update:content', editorInstance.getMarkdown())
  })
})

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