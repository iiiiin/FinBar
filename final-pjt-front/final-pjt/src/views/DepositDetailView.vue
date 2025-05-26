<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <NavigationBar />

    <v-row class="my-4">
      <v-col cols="12">
        <Title :title="product.fin_prdt_nm || '상세 정보'" />
      </v-col>
    </v-row>

    <!-- 북마크 버튼 -->
    <v-row class="mb-4">
      <v-col cols="12" class="text-right">
        <v-btn
          :color="isBookmarked ? 'error' : 'primary'"
          @click="toggleBookmark"
          :loading="bookmarkLoading"
        >
          {{ isBookmarked ? '북마크 취소' : '북마크 추가' }}
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

    <!-- Vuetify Snackbar for notifications -->
    <v-snackbar v-model="snackbar.show" :timeout="snackbar.timeout" top right>
      {{ snackbar.message }}
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
        message: '',
        timeout: 3000
      }
    }
  },
  computed: {
    optionHeaders() {
      return [
        { text: '금리 유형',   value: 'intr_rate_type_nm' },
        { text: '저축 기간',   value: 'save_trm' },
        { text: '금리1',       value: 'intr_rate' },
        { text: '금리2',       value: 'intr_rate2' },
      ]
    }
  },
  async mounted() {
    this.loading = true
    const id = this.$route.params.id
    try {
      const res = await axios.get(`http://127.0.0.1:8000/products/deposits/${id}/`)
      this.product = res.data
      await this.checkBookmark()
    } catch (e) {
      console.error(e)
      this.notify('상세정보를 불러오던 중 오류가 발생했습니다.')
    } finally {
      this.loading = false
    }
  },
  methods: {
    async checkBookmark() {
      try {
        const res = await axios.get('http://127.0.0.1:8000/bookmarks/deposits/')
        const list = Array.isArray(res.data) ? res.data : (res.data.results || [])
        const bookmark = list.find(b => b.deposit_product && b.deposit_product.id === this.product.id)
        if (bookmark) {
          this.isBookmarked = true
          this.bookmarkId = bookmark.id
        }
      } catch (e) {
        console.warn('북마크 조회 실패', e)
      }
    },
    watch: {
  '$route.params.id': {
    immediate: true,
    handler(newId) {
      this.resetBookmarkState()
      this.loadProduct(newId)
    }
  }
},
resetBookmarkState() {
    this.isBookmarked = false
    this.bookmarkId = null
  },
  async loadProduct(id) {
    // 상품 fetch 후
    await this.checkBookmark()
  },
    async toggleBookmark() {
      if (this.bookmarkLoading) return
      this.bookmarkLoading = true
      const id = this.$route.params.id

      try {
        if (!this.isBookmarked) {
          const res = await axios.post(
            'http://127.0.0.1:8000/bookmarks/deposits/',
            { deposit_product_id: id }
          )
          this.isBookmarked = true
          this.bookmarkId = res.data.id
          this.notify('북마크에 추가되었습니다.')
        } else {
          await axios.delete(
            `http://127.0.0.1:8000/bookmarks/deposits/${this.bookmarkId}/`
          )
          this.isBookmarked = false
          this.bookmarkId = null
          this.notify('북마크가 취소되었습니다.')
        }
      } catch (e) {
        console.error('북마크 처리 오류:', e.response?.data || e)
        this.notify('북마크 처리 중 오류가 발생했습니다.')
      } finally {
        this.bookmarkLoading = false
      }
    },
    notify(message) {
      this.snackbar.message = message
      this.snackbar.show = true
    }
  }
}
</script>

<style scoped>
/* 필요 시 스타일 추가 */
</style>
