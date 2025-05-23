<template>
  <v-row justify="center" class="pagination-wrapper">
    <v-pagination
      v-model="current"
      :length="total"
      @update:modelValue="onPage"
      circle
      total-visible="7"
    />
  </v-row>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  page:  { type: Number, required: true },
  total: { type: Number, required: true }
})
const emits = defineEmits(['change'])

// 내부 상태 관리
const current = ref(props.page)

// props.page 변경 시 내부 current 업데이트
watch(
  () => props.page,
  val => { current.value = val }
)

// 페이지 변경 시 이벤트 발생
function onPage(val) {
  emits('change', val)
}
</script>

<style scoped>
.pagination-wrapper {
  margin-top: 16px;
}
</style>
