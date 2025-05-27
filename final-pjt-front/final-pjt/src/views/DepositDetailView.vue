<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <NavigationBar />

    <v-row class="my-4" align="center">
      <v-col cols="10">
        <Title :title="product.fin_prdt_nm || '상세 정보'" />
      </v-col>
      <v-col cols="2" class="text-right">
        <!-- 북마크 상태에 따라 텍스트 토글 -->
        <v-btn
          color="black"
          class="white--text"
          @click="toggleBookmark"
          :loading="bookmarkLoading"
        >
          {{ isBookmarked ? '가입취소' : '가입' }}
        </v-btn>
      </v-col>
    </v-row>

    <v-card elevation="2" class="mb-6">
      <v-card-text>
        <div><strong>은행명:</strong> {{ product.kor_co_nm }}</div>
        <div><strong>상품코드:</strong> {{ product.fin_prdt_cd }}</div>
        <div><strong>가입방식:</strong> {{ product.join_way }}</div>
        <div><strong>만기이자:</strong> {{ product.mtrt_int }}</div>
        <div><strong>특약조건:</strong> {{ product.spcl_cnd }}</div>
        <div><strong>가입제한:</strong> {{ product.join_deny }}</div>
        <div><strong>가입대상:</strong> {{ product.join_member }}</div>
        <div><strong>기타:</strong> {{ product.etc_note }}</div>
        <div><strong>최대한도:</strong> {{ product.max_limit }}</div>
        <div><strong>공시시작일:</strong> {{ product.dcls_strt_day }}</div>
      </v-card-text>
    </v-card>

    <v-data-table
      :headers="optionHeaders"
      :items="product.options"
      class="elevation-1"
      item-key="deposit_product_id"
    >
      <template #item.intr_rate="{ item }">
        {{ item.intr_rate }}%
      </template>
    </v-data-table>

    <v-snackbar
      v-model="snackbar.show"
      :timeout="snackbar.timeout"
      :color="snackbar.color"
      top
      right
    >
      {{ snackbar.text }}
      <template #action>
        <v-btn text @click="snackbar.show = false">닫기</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script>
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title from '@/components/Title.vue'
import { useAuthStore } from '@/stores/auth'


export default {
  name: 'DepositDetailView',
  components: { NavigationBar, Title },
  data() {
    return {
      product: {},
      loading: false,
      isBookmarked: false,
      bookmarkId: null,
      bookmarkLoading: false,
      snackbar: {
        show: false,
        text: '',
        color: 'grey lighten-2',
        timeout: 3000,
      },
    }
  },
  computed: {
    optionHeaders() {
      return [
        { text: '금리 유형', value: 'intr_rate_type_nm' },
        { text: '저축 기간', value: 'save_trm' },
        { text: '금리1', value: 'intr_rate' },
        { text: '금리2', value: 'intr_rate2' },
      ]
    },
  },
  async mounted() {
    this.loading = true
    const productId = Number(this.$route.params.id)
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/products/deposits/${productId}/`
      )
      this.product = res.data
      await this.fetchBookmarkStatus(productId)
    } catch (e) {
      console.error('상품 상세 조회 오류', e)
      this.showSnackbar('상세정보를 불러오던 중 오류가 발생했습니다.', 'error')
    } finally {
      this.loading = false
    }
  },
  methods: {
    showSnackbar(message, color = 'primary') {
      this.snackbar.text = message
      this.snackbar.color = color
      this.snackbar.show = true
    },
    async fetchBookmarkStatus(productId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token
        if (!token) return
        const res = await axios.get(
          'http://127.0.0.1:8000/bookmarks/deposits/',
          { headers: { Authorization: `Token ${token}` } }
        )
        // 페이징 객체인 경우 results 사용, 배열이면 그대로
        const data = Array.isArray(res.data)
          ? res.data
          : res.data.results || []
        // BookmarkSerializer 에서 read-only로 반환되는 필드를 확인
        // deposit_product_id가 없다면 nested deposit_product.fin_prdt_cd로 매칭
        const found = data.find(
          b =>
            b.deposit_product_id === productId ||
            b.deposit_product?.fin_prdt_cd === this.product.fin_prdt_cd
        )
        if (found) {
          this.isBookmarked = true
          this.bookmarkId = found.id
        }
      } catch (e) {
        console.error('북마크 상태 조회 오류', e)
      }
    },
    async toggleBookmark() {
      const authStore = useAuthStore()
      const token = authStore.token
      if (!token) {
        this.showSnackbar('로그인이 필요합니다.', 'info')
        return
      }

      this.bookmarkLoading = true
      const productId = Number(this.$route.params.id)
      try {
        if (this.isBookmarked) {
          await axios.delete(
            `http://127.0.0.1:8000/bookmarks/deposits/${this.bookmarkId}/`,
            { headers: { Authorization: `Token ${token}` } }
          )
          this.isBookmarked = false
          this.bookmarkId = null
          this.showSnackbar('가입이 취소되었습니다.', 'grey lighten-2')
        } else {
          const res = await axios.post(
            'http://127.0.0.1:8000/bookmarks/deposits/',
            { deposit_product_id: productId },
            { headers: { Authorization: `Token ${token}` } }
          )
          this.isBookmarked = true
          this.bookmarkId = res.data.id
          this.showSnackbar('가입 되었습니다.', 'grey lighten-2')
        }
      } catch (e) {
        console.error('북마크 토글 오류', e.response?.data || e)
        this.showSnackbar('북마크 처리 중 오류가 발생했습니다.', 'error')
      } finally {
        this.bookmarkLoading = false
      }
    },
  }
}
</script>

<style scoped>
/* 필요 시 스타일 추가 */
</style>
