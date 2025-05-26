<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <NavigationBar />

    <v-row class="my-4">
      <v-col cols="12">
        <Title :title="product.fin_prdt_nm || '상세 정보'" />
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
  </v-container>
</template>

<script>
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title from '@/components/Title.vue'

export default {
  name: 'SavingDetailView',
  components: { NavigationBar, Title },
  data() {
    return {
      product: {},
      loading: false,
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
    try {
      const id = this.$route.params.id
      const res = await axios.get(`http://127.0.0.1:8000/products/savings/${id}/`)
      this.product = res.data
      // console.log(res)
    } catch (e) {
      console.error(e)
      this.$toast.error('상세정보를 불러오던 중 오류가 발생했습니다.')
    } finally {
      this.loading = false
    }
  }
}
</script>

<style scoped>
/* 필요 시 스타일 추가 */
</style>
