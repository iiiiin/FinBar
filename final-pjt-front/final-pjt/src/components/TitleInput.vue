<template>
  <v-text-field
    v-model="input"
    label="제목"
    dense
    outlined
    placeholder="게시글 제목"
  />
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' }
})
const emits = defineEmits(['update:modelValue'])

const input = ref(props.modelValue)

// 부모 props 변경 시 내부 업데이트
watch(
  () => props.modelValue,
  val => { input.value = val }
)
// 내부 값 변경 시 부모에게 emit
watch(input, val => {
  emits('update:modelValue', val)
})
</script>

<style scoped>
.v-text-field {
  margin-bottom: 16px;
}
</style>