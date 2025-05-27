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

    <div v-if="loading" class="loading-images">
      <img
        :src="loadingImages[currentLoadingIndex]"
        alt="로딩 중"
        class="loading-img"
      />
    </div>

    <!-- 결과 테이블 -->
    <v-data-table
      :headers="headers"
      :items="loading ? [] : paginatedItems"
      :loading="loading"
      class="elevation-1"
      item-key="key"
      fixed-header
      height="400px"
      hide-default-footer
    >


      <!-- 상품명 컬럼: 클릭 시 상세 페이지로 이동 -->
      <template #item.finPrdtNm="{ item }">
        <router-link :to="detailRoute(item)">
           {{ item.finPrdtNm }}
        </router-link>
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
    <PlaceFooter src="/images/plate.png" alt="메뉴접시" />
  </v-container>
  
</template>

<script>
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title from '@/components/Title.vue'
import Pagination from '@/components/Pagination.vue'
import PlaceFooter from '@/components/PlaceFooter.vue'

export default {
  name: 'ProductListView',
  components: { NavigationBar, Title, Pagination, PlaceFooter },
  data() {
    return {
      type: 'deposit',               // 예금/적금 상태
      rawProducts: [],               // API에서 받아온 데이터
      filters: { bank: null, term: null },
      loading: false,
      loadingImages: [
        'images/shaker1.png',
        'images/shaker2.png'
      ],
      currentLoadingIndex: 0,
      _loadingTimer: null,
      currentPage: 1,                // 현재 페이지
      perPage: 10,                   // 페이지당 항목 수
    }
  },
  watch: {
    loading(newVal) {
      if (newVal) {
        // 로딩 시작 시 500ms마다 인덱스 업데이트
        this._loadingTimer = setInterval(() => {
          this.currentLoadingIndex =
            (this.currentLoadingIndex + 1) % this.loadingImages.length
        }, 500)
      } else {
        // 로딩 끝나면 타이머 해제, 인덱스 초기화
        clearInterval(this._loadingTimer)
        this.currentLoadingIndex = 0
      }
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
            finCoNo:         product.fin_co_no,
            korCoNm:         product.kor_co_nm,
            finPrdtCd:       product.fin_prdt_cd,
            finPrdtNm:       product.fin_prdt_nm,
            joinWay:         product.join_way,
            mtrtInt:         product.mtrt_int,
            spclCnd:         product.spcl_cnd,
            joinDeny:        product.join_deny,
            joinMember:      product.join_member,
            etcNote:         product.etc_note,
            maxLimit:        product.max_limit,
            dclsStrtDay:     product.dcls_strt_day,

            // DepositProductOptions
            depositProductId: opt.deposit_product_id,
            savingProductId: opt.saving_product_id,
            intrRateTypeNm:   opt.intr_rate_type_nm,
            saveTrm:          opt.save_trm,
            intrRate:         opt.intr_rate,
            intrRate2:        opt.intr_rate2,
          })
        })
        return acc
      }, [])
    },
    // 필터 적용
    filteredItems() {
      return this.optionsFlatten.filter(item =>
        (!this.filters.bank || item.korCoNm === this.filters.bank) &&
        (!this.filters.term || item.saveTrm === this.filters.term)
      )
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
        { text: '공시 시작일', value: 'dclsStrtDay' },
        { text: '은행명',       value: 'korCoNm' },
        { text: '상품명',       value: 'finPrdtNm' },
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
   /**
    * 예금/적금 모드에 따라
    * DepositDetail 또는 SavingDetail 로 이동할 라우트 객체 반환
    */
   detailRoute(item) {
    if (this.type === 'deposit') {
      return { name: 'depositDetail', params: { id: item.depositProductId } }
    } else {
      return { name: 'savingDetail',  params: { id: item.savingProductId  } }
    }
  },
    async fetchProducts() {
      this.loading = true
      try {
        const url = this.type === 'deposit'
          ? 'http://127.0.0.1:8000/products/deposits/'
          : 'http://127.0.0.1:8000/products/savings/'
        const res = await axios.get(url)
        const data = Array.isArray(res.data)
          ? res.data
          : res.data.results || []
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
.plate-footer {
  max-width: 800px;    /* v-container 와 동일 너비 */
  margin: 0 auto;      /* 가운데 정렬 */
}
.plate-img {
  display: block;      /* inline-block 여백 제거 */
  width: 100%;         /* 부모(plate-footer) 폭에 딱 맞춤 */
  height: auto;        /* 원본 비율 유지 */
}
/* Vuetify v-btn 기본 스타일 오버라이드 */
::v-deep .v-btn {
  background-color: #ffffff !important;       /* 흰 배경 */
  color: #000000 !important;                  /* 검은 글씨 */
  box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important; /* 연한 회색 그림자 */
  border: none !important;                    /* 테두리 제거 */
}

/* Hover 시 그림자만 살짝 강조 */
::v-deep .v-btn:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

/* 선택된(primary) 혹은 text prop 은 그대로 두고, 색만 바뀌게 */
::v-deep .v-btn--text {
  background-color: transparent !important;
  box-shadow: none !important;
  color: #000000 !important;
}
.loading-images {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px; /* 원하는 높이만큼 */
}

.loading-img {
  width: 120px;
  height: auto;
}
</style>
