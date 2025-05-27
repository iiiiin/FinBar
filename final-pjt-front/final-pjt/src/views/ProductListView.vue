<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <NavigationBar />

    <v-row class="my-4">
      <v-col cols="12">
        <Title title="예·적금 정보 조회" />
      </v-col>
    </v-row>

    <!-- 토글 -->
    <v-row class="mb-4" dense>
      <v-col cols="6">
        <v-btn
          :color="type==='deposit'?'primary':'grey lighten-1'"
          block
          @click="changeType('deposit')"
        >예금</v-btn>
      </v-col>
      <v-col cols="6">
        <v-btn
          :color="type==='saving'?'primary':'grey lighten-1'"
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

    <!-- 로딩 -->
    <LoadingSpinner
      v-if="loading"
      :images="loadingImages"
      :interval="100"
    />

    <!-- 결과 테이블 -->
    <v-data-table
      :headers="headers"
      :items="paginatedItems"
      :loading="loading"
      class="elevation-1"
      item-key="key"
      fixed-header
      height="400"
      hide-default-footer
    >
      <!-- 상품명 클릭 이동 -->
      <template #item.finPrdtNm="{ item }">
        <span v-if="detailRoute(item).params.id">
          <router-link :to="detailRoute(item)">
            
            {{ item.finPrdtNm }}
          </router-link>
        </span>
        <span v-else>
          {{ item }}
          {{ item.finPrdtNm }}
        </span>
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
import NavigationBar from '@/components/NavigationBar.vue'
import Title from '@/components/Title.vue'
import Pagination from '@/components/Pagination.vue'
import PlaceFooter from '@/components/PlaceFooter.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import apiClient from '@/services/api'

export default {
  name: 'ProductListView',
  components: {
    NavigationBar,
    Title,
    Pagination,
    PlaceFooter,
    LoadingSpinner,
  },
  data() {
    return {
      type: 'deposit',
      rawProducts: [],
      totalCount: 0,
      filters: { bank: null, term: null },
      loading: false,
      loadingImages: ['images/shaker1.png','images/shaker2.png'],
      currentPage: 1,
      perPage: 10,
    }
  },
  computed: {
    rowItems() {
      return this.rawProducts.map(prod => {
        const row = {
          key: prod.fin_prdt_cd,
          depositProductId: prod.deposit_product_id,
          savingProductId: prod.saving_product_id,
          dclsStrtDay: prod.dcls_strt_day,
          korCoNm: prod.kor_co_nm,
          finPrdtNm: prod.fin_prdt_nm,
          rate3:  '-', rate6:  '-', rate12: '-', rate24: '-',
        }
        if (Array.isArray(prod.options)) {
          prod.options.forEach(opt => {
            const v = opt.intr_rate2 != null ? opt.intr_rate2 : '-'
            switch (opt.save_trm) {
              case '3':  row.rate3  = v; break
              case '6':  row.rate6  = v; break
              case '12': row.rate12 = v; break
              case '24': row.rate24 = v; break
            }
          })
        }
        return row
      })
    },
    paginatedItems() {
      return this.rowItems
    },
    totalPages() {
      return Math.ceil(this.totalCount / this.perPage) || 1
    },
    headers() {
      return [
        { title: '공시 시작일', key: 'dclsStrtDay' },
        { title: '은행명',       key: 'korCoNm'   },
        { title: '상품명',       key: 'finPrdtNm' },
        { title: '3개월',        key: 'rate3'     },
        { title: '6개월',        key: 'rate6'     },
        { title: '12개월',       key: 'rate12'    },
        { title: '24개월',       key: 'rate24'    },
      ]
    },
    bankItems() {
      return [...new Set(this.rowItems.map(r => r.korCoNm))]
    },
    termItems() {
      return ['3','6','12','24']
    },
  },
  methods: {
    changeType(newType) {
      this.currentPage = 1
      this.type = newType
      this.fetchProducts(1)
    },
    detailRoute(item) {
      const id = this.type === 'deposit'
        ? item.depositProductId
        : item.savingProductId
      return { name: this.type==='deposit'?'depositDetail':'savingDetail', params: { id }}
    },
    async fetchProducts(page = 1) {
      this.loading = true
      this.currentPage = page
      try {
        const url = this.type === 'deposit'
          ? '/products/deposits/'
          : '/products/savings/'
        const params = {
          page,
          page_size: this.perPage,
          kor_co_nm: this.filters.bank,
        }
        if (this.filters.term) {
          params[ this.type==='deposit'
            ? 'depositproductoptions__save_trm'
            : 'savingproductoptions__save_trm' ] = this.filters.term
        }
        const res = await apiClient.get(url, { params })
        this.rawProducts = res.data.results || []
        this.totalCount   = res.data.count || 0
      } catch (e) {
        console.error(e)
        this.$toast.error('데이터 조회 중 오류가 발생했습니다.')
      } finally {
        this.loading = false
      }
    },
    applyFilters() {
      this.fetchProducts(1)
    },
    onPageChange(page) {
      this.fetchProducts(page)
    },
  },
  mounted() {
    this.fetchProducts()
  },
}
</script>

<style scoped>
.loading-images {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
.loading-img {
  width: 120px;
  height: auto;
}
</style>