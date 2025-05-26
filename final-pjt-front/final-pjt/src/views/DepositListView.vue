<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <!-- 네비게이션 바 -->
    <NavigationBar />

    <!-- 페이지 제목: 고정된 타이틀 -->
    <v-row class="my-4">
      <v-col cols="12">
        <Title title="예·적금 정보 조회" />
      </v-col>
    </v-row>

    <!-- 예금/적금 토글 -->
    <v-row class="mb-4" dense>
      <v-col cols="6">
        <v-btn
          :color="type === 'deposit' ? 'primary' : 'grey lighten-1'"
          block
          @click="changeType('deposit')"
        >예금</v-btn>
      </v-col>
      <v-col cols="6">
        <v-btn
          :color="type === 'saving' ? 'primary' : 'grey lighten-1'"
          block
          @click="changeType('saving')"
        >적금</v-btn>
      </v-col>
    </v-row>

    <!-- 필터 -->
    <v-row align="center" class="mb-4" dense>
      <v-col cols="12" sm="4">
        <v-select
          v-model="filters.bank"
          :items="bankItems"
          label="은행 선택"
          clearable
        />
      </v-col>
      <v-col cols="12" sm="4">
        <v-select
          v-model="filters.term"
          :items="termItems"
          label="기간(개월)"
          clearable
        />
      </v-col>
      <v-col cols="12" sm="4">
        <v-btn block color="primary" @click="applyFilters">확인</v-btn>
      </v-col>
    </v-row>

    <!-- 결과 테이블 -->
    <v-data-table
      :headers="headers"
      :items="paginatedItems"
      :loading="loading"
      class="elevation-1"
      :items-per-page="perPage"
      item-key="key"
    >
      <!-- 커스텀 헤더 슬롯: props.headers로 헤더 행 렌더링 -->
      <template #header="{ props }">
        <tr>
          <th v-for="h in props.headers" :key="h.value" class="text-left">
            {{ h.text }}
          </th>
        </tr>
      </template>

      <!-- 금리1 포맷을 위한 슬롯 -->
      <template #item.intrRate="{ item }">
        {{ item.intrRate }}%
      </template>
    </v-data-table>

    <!-- 페이지네이션 -->
    <Pagination
      :page="currentPage"
      :total="totalPages"
      @change="onPageChange"
    />
  </v-container>
</template>

<script>
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title from '@/components/Title.vue'
import Pagination from '@/components/pagination.vue'

export default {
  name: 'DepositListView',
  components: { NavigationBar, Title, Pagination },
  data() {
    return {
      type: 'deposit',               // 예금/적금 상태
      rawProducts: [],               // API에서 받아온 데이터
      filters: { bank: null, term: null },
      loading: false,
      currentPage: 1,                // 현재 페이지
      perPage: 10,                   // 페이지당 항목 수
    }
  },
  computed: {
    // API 데이터 평탄화: DepositProduct + DepositProductOptions 필드 모두 포함
    optionsFlatten() {
      return this.rawProducts.reduce((acc, product) => {
        (product.options || []).forEach(opt => {
          acc.push({
            // 고유 키
            key: `${product.fin_prdt_cd}_${opt.intr_rate_type_nm}_${opt.save_trm}`,
            // DepositProduct
            finCoNo: product.fin_co_no,
            korCoNm: product.kor_co_nm,
            finPrdtCd: product.fin_prdt_cd,
            finPrdtNm: product.fin_prdt_nm,
            joinWay: product.join_way,
            mtrtInt: product.mtrt_int,
            spclCnd: product.spcl_cnd,
            joinDeny: product.join_deny,
            joinMember: product.join_member,
            etcNote: product.etc_note,
            maxLimit: product.max_limit,
            dclsStrtDay: product.dcls_strt_day,
            // DepositProductOptions
            depositProductId: opt.deposit_product_id,
            intrRateTypeNm: opt.intr_rate_type_nm,
            saveTrm: opt.save_trm,
            intrRate: opt.intr_rate,
            intrRate2: opt.intr_rate2,
          })
        })
        return acc
      }, [])
    },
    // 필터 적용
    filteredItems() {
      return this.optionsFlatten.filter(item => (
        (!this.filters.bank || item.korCoNm === this.filters.bank) &&
        (!this.filters.term || item.saveTrm === this.filters.term)
      ))
    },
    // 전체 페이지 수
    totalPages() {
      return Math.ceil(this.filteredItems.length / this.perPage) || 1
    },
    // 현재 페이지 아이템
    paginatedItems() {
      const start = (this.currentPage - 1) * this.perPage
      return this.filteredItems.slice(start, start + this.perPage)
    },
    // 테이블 헤더 정의
    headers() {
      return [
        { text: '금융회사 코드', value: 'finCoNo' },
        { text: '은행명',       value: 'korCoNm' },
        { text: '상품 코드',     value: 'finPrdtCd' },
        { text: '상품명',       value: 'finPrdtNm' },
        { text: '가입 방식',     value: 'joinWay' },
        { text: '만기 이자',     value: 'mtrtInt' },
        { text: '특약 조건',     value: 'spclCnd' },
        { text: '가입 제한',     value: 'joinDeny' },
        { text: '가입 대상',     value: 'joinMember' },
        { text: '기타 내용',     value: 'etcNote' },
        { text: '최대 한도',     value: 'maxLimit' },
        { text: '공시 시작일',   value: 'dclsStrtDay' },
        { text: '옵션 ID',       value: 'depositProductId' },
        { text: '금리 유형',     value: 'intrRateTypeNm' },
        { text: '저축 기간',     value: 'saveTrm' },
        { text: '금리1',         value: 'intrRate' },
        { text: '금리2',         value: 'intrRate2' },
      ]
    },
    // 필터 옵션
    bankItems() {
      return [...new Set(this.optionsFlatten.map(i => i.korCoNm))]
    },
    termItems() {
      return [...new Set(this.optionsFlatten.map(i => i.saveTrm))]
    },
  },
  methods: {
    changeType(newType) {
      if (this.type !== newType) {
        this.type = newType
        this.fetchProducts()
      }
    },
    async fetchProducts() {
      this.loading = true
      try {
        const url = this.type === 'deposit'
          ? 'http://127.0.0.1:8000/products/deposits/'
          : 'http://127.0.0.1:8000/products/savings/'
        const res = await axios.get(url)
        const data = Array.isArray(res.data) ? res.data : res.data.results || []
        this.rawProducts = data
        this.filters.bank = null
        this.filters.term = null
        this.currentPage = 1
      } catch (e) {
        console.error(e)
        this.$toast.error('데이터 조회 중 오류가 발생했습니다.')
      } finally {
        this.loading = false
      }
    },
    applyFilters() {
      this.currentPage = 1
    },
    onPageChange(page) {
      this.currentPage = page
    },
  },
  mounted() {
    this.fetchProducts()
  },
}
</script>

<style scoped>
/* 추가 스타일 필요 시 작성 */
</style>
