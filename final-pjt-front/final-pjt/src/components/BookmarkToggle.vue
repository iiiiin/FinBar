<template>
  <v-btn
    color="black"
    class="white--text"
    @click="onClick"
    :loading="loading"
  >
    {{ toggled ? offText : onText }}
  </v-btn>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  // 초기 토글 상태 (북마크 여부)
  initialToggled: Boolean,
  // 버튼에 표시할 텍스트
  onText:  { type: String, default: '가입' },
  offText: { type: String, default: '가입취소' },
  // 현재 북마크 ID (삭제할 때 사용)
  bookmarkId: { type: Number, default: null },
  resourceId: { type: Number, required: true },
  // axios 인스턴스 등 API 호출 클라이언트
  apiClient: { type: [Object, Function], required: true },
  // ex) "http://127.0.0.1:8000/bookmarks/deposits"
  baseUrl: { type: String, required: true },
})
const emit = defineEmits([
  'update:toggled',     // 부모로 토글 상태 전달
  'update:bookmarkId',  // 부모로 새 북마크 ID 전달
  'snackbar',           // 스낵바 메시지 전달
])

const toggled = ref(props.initialToggled)
const loading = ref(false)

// 부모에서 초기 상태가 바뀌면 내부 토글 상태도 동기화
watch(() => props.initialToggled, v => toggled.value = v)

async function onClick() {
  loading.value = true
  try {
    if (toggled.value) {
      // 북마크 삭제
      await props.apiClient.delete(
        `${props.baseUrl}/${props.bookmarkId}/`
      )
      toggled.value = false
      emit('update:bookmarkId', null)
      emit('snackbar', { text: '가입이 취소되었습니다.', color: 'grey lighten-2' })

    } else {
      // 북마크 생성 (POST)
      const key = props.baseUrl.endsWith('deposits')
        ? 'deposit_product_id'
        : props.baseUrl.endsWith('savings')
          ? 'saving_product_id'
          : 'stock_product_id'
      const res = await props.apiClient.post(
        `${props.baseUrl}/`,
        { [key]: Number(props.resourceId) }
      )
      toggled.value = true
      emit('update:bookmarkId', res.data.id)
      emit('snackbar', { text: '가입 되었습니다.', color: 'grey lighten-2' })
    }
    emit('update:toggled', toggled.value)

  } catch (e) {
    emit('snackbar', { text: '북마크 처리 중 오류가 발생했습니다.', color: 'error' })
  } finally {
    loading.value = false
  }
}
</script>
