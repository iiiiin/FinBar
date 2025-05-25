<!-- src/views/BankMapView.vue -->
<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <!-- 1. 네비게이션 바 -->
    <v-row>
      <v-col cols="12">
        <NavigationBar />
      </v-col>
    </v-row>

    <!-- 2. 페이지 제목 -->
    <v-row class="my-4">
      <v-col cols="12">
        <Title :title="pageTitle" />
      </v-col>
    </v-row>

    <!-- 3. 필터(select) + 확인 버튼 / 지도 영역 -->
    <v-row>
      <!-- 3-1. 왼쪽: 필터 영역 (시/도, 구/군, 은행 선택 + 확인 버튼) -->
      <v-col cols="12" md="3">
        <!-- 시/도 선택 -->
        <v-select
          v-model="selectedSido"
          :items="sidoOptions"
          item-text="name"
          item-value="code"
          label="시/도 선택"
          dense
          @change="onSidoChange"
        />

        <!-- 구/군 선택 (시/도 선택 후 활성화) -->
        <v-select
          v-model="selectedGugun"
          :items="gugunOptions"
          item-text="name"
          item-value="code"
          label="구/군 선택"
          dense
          :disabled="!selectedSido"
        />

        <!-- 은행 선택 (구/군 선택 후 활성화) -->
        <v-select
          v-model="selectedBank"
          :items="bankOptions"
          label="은행 선택"
          dense
          :disabled="!selectedGugun"
        />

        <!-- 선택된 조건으로 검색 -->
        <v-btn
          block
          color="primary"
          class="mt-4"
          @click="onSearch"
        >
          검색
        </v-btn>
      </v-col>

      <!-- 3-2. 오른쪽: Kakao 지도 렌더링 영역 -->
      <v-col cols="12" md="9">
        <!-- 지도가 그려질 div -->
        <div id="map" class="map-container"></div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import NavigationBar from '@/components/NavigationBar.vue'
import Title         from '@/components/Title.vue'

/** 페이지 타이틀 */
const pageTitle = '주변 은행 검색'

/** ————————————— 변수 선언 ————————————— */
/** 1) 셀렉트박스 옵션 (API 프록시를 통해 백엔드에서 가져옴) */
const sidoOptions  = ref([])   // [{ code: '11', name: '서울특별시' }, …]
const gugunOptions = ref([])   // [{ code: '110', name: '강남구' }, …]
const bankOptions  = [         // 은행명은 고정 리스트로도, API에서 가져와도 됩니다.
  '국민은행',
  '기업은행',
  '신한은행',
  '하나은행',
  // … 필요시 추가
]

/** 2) 사용자가 선택한 값 */
const selectedSido  = ref(null)
const selectedGugun = ref(null)
const selectedBank  = ref(null)

/** 3) 서버(백엔드)에서 받아온 은행 위치 리스트 */
const banks = ref([])  // [{ name: '국민은행 강남지점', lat: 37.498, lng: 127.027 }, …]

/** 4) Kakao Map 객체 참조용 */
let kakaoMap = null

/** ————————————— helper 함수 ————————————— */

/**
 * 1) 컴포넌트 마운트 시:
 *    - 시/도 목록을 가져오고
 *    - 기본 지도는 서울 중심으로 한 번 초기화
 */
onMounted(async () => {
  await fetchSidoList()
  initMap(37.5665, 126.9780)  // 서울시청 좌표 예시
})

/**
 * 2) 시/도 목록 가져오기
 *    - 프론트엔드 → 백엔드(/api/regions/sido) → 카카오 REST API 호출(프록시)
 */
async function fetchSidoList() {
  try {
    const { data } = await axios.get('/api/regions/sido')
    sidoOptions.value = data
  } catch (e) {
    console.error('시/도 조회 실패', e)
  }
}

/**
 * 3) 시/도 선택 시 구/군 목록 가져오기
 */
async function onSidoChange(code) {
  selectedGugun.value = null
  gugunOptions.value = []
  try {
    const { data } = await axios.get('/api/regions/gugun', {
      params: { sido: code }
    })
    gugunOptions.value = data
  } catch (e) {
    console.error('구/군 조회 실패', e)
  }
}

/**
 * 4) “확인” 버튼 클릭 → 은행 검색
 *    - 파라미터(selectedGugun, selectedBank) 기준으로
 *      백엔드(/api/banks/search)에서 가까운 은행 리스트를 받아옴
 *    - 받은 좌표를 Kakao Map 위에 마커로 표시
 */
async function onSearch() {
  if (!selectedGugun.value || !selectedBank.value) return

  try {
    const { data } = await axios.get('/api/banks/search', {
      params: {
        gugun: selectedGugun.value,
        bank:  selectedBank.value
      }
    })
    banks.value = data
    placeMarkers()
  } catch (e) {
    console.error('은행 검색 실패', e)
  }
}

/**
 * 5) 지도 초기화
 *    - SDK 스크립트는 index.html에서 도메인 제한 설정된 JS Key로 로드되어 있어야 함
 */
function initMap(lat, lng) {
  kakao.maps.load(() => {
    const container = document.getElementById('map')
    const options = {
      center: new kakao.maps.LatLng(lat, lng),
      level: 4  // 지도의 확대 레벨
    }
    kakaoMap = new kakao.maps.Map(container, options)
  })
}

/**
 * 6) banks 배열을 순회하며 마커를 찍고, Bounds에 맞춰 줌
 */
function placeMarkers() {
  if (!kakaoMap) return

  const bounds = new kakao.maps.LatLngBounds()
  // 기존 마커는 지우고 싶으면, 마커 배열을 관리해두고 setMap(null) 처리 필요

  banks.value.forEach(bank => {
    const pos = new kakao.maps.LatLng(bank.lat, bank.lng)
    new kakao.maps.Marker({
      map: kakaoMap,
      position: pos,
      title: bank.name
    })
    bounds.extend(pos)
  })

  // 모든 마커가 보이도록 지도의 중심·레벨을 자동 조정
  kakaoMap.setBounds(bounds)
}
</script>

<style scoped>
/* 지도 영역 크기 고정 */
.map-container {
  width: 100%;
  height: 400px;
  border: 1px solid #ddd;
}
</style>
