<!-- src/views/BankMapView.vue -->
<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <!-- 네비게이션 바 -->
    <v-row>
      <v-col cols="12">
        <NavigationBar />
      </v-col>
    </v-row>

    <!-- 페이지 제목 -->
    <v-row class="my-4">
      <v-col cols="12">
        <Title :title="pageTitle" />
      </v-col>
    </v-row>

    <!-- 배경 이미지 영역 시작 -->
    <div class="map-background">
      <!-- 필터 + 지도 영역 -->
      <v-row>
        <v-col cols="12" md="3">
          <!-- 시/도 선택 -->
          <v-select
            v-model="selectedSido"
            :items="sidoList"
            label="시/도 선택"
            dense
            @update:model-value="onSidoChange"
          />

          <!-- 구/군 선택 -->
          <v-select
            v-if="selectedSido"
            v-model="selectedGugun"
            :items="gugunList"
            label="구/군 선택"
            dense
            @update:model-value="onGugunChange"
          />

          <!-- 은행 선택 -->
          <v-select
            v-if="selectedGugun"
            v-model="selectedBank"
            :items="bankOptions"
            label="은행 선택"
            dense
          />

          <!-- 검색 버튼 -->
          <v-btn
            block
            color="primary"
            class="mt-4"
            @click="onSearch"
            :disabled="!selectedBank"
          >
            검색
          </v-btn>
        </v-col>

        <!-- 지도 렌더링 영역 -->
        <v-col cols="12" md="9">
          <div id="map" class="map-container"></div>
        </v-col>
      </v-row>
    </div>
    <!-- 배경 이미지 영역 끝 -->

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NavigationBar from '@/components/NavigationBar.vue'
import Title from '@/components/Title.vue'

/** 페이지 타이틀 */
const pageTitle = '주변 은행 검색'

/** 지역 리스트 */
const sidoList = ref([])
const gugunList = ref([])

/** 선택 값 */
const selectedSido = ref(null)
const selectedGugun = ref(null)

/** 은행 리스트 */
const bankOptions = ['국민은행', '기업은행', '신한은행', '하나은행']
const selectedBank = ref(null)

/** 검색 결과 장소 */
const banks = ref([])

/** Kakao 맵, Places, 마커 저장 */
let kakaoMap = null
let placesService = null
let markers = []

/** Kakao SDK 로드 */
function loadKakaoMapSdk() {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps && window.kakao.maps.services) {
      return resolve()
    }
    const script = document.createElement('script')
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_JS_KEY}&libraries=services&autoload=false`
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Kakao Maps SDK 로드 실패'))
    document.head.appendChild(script)
  })
}

/** 행정구역 JSON 로드 */
async function loadRegions() {
  try {
    const res = await fetch('/korea-administrative-district.json')
    const { data } = await res.json()
    sidoList.value = data.map(item => Object.keys(item)[0])
  } catch (e) {
    console.error('행정구역 로드 실패', e)
  }
}

/** 시/도 변경 */
function onSidoChange(code) {
  fetch('/korea-administrative-district.json')
    .then(r => r.json())
    .then(json => {
      const entry = json.data.find(it => Object.keys(it)[0] === code)
      const list = entry ? entry[code] : []
      gugunList.value = list
      selectedGugun.value = null
      selectedBank.value = null
      banks.value = []
    })
    .catch(e => console.error('구/군 로드 실패', e))
}

/** 구/군 변경 */
function onGugunChange(code) {
  selectedBank.value = null
  banks.value = []
}

/** 지도 초기화 및 Places 서비스 설정 */
function initMap(lat, lng) {
  kakao.maps.load(() => {
    const container = document.getElementById('map')
    kakaoMap = new kakao.maps.Map(container, {
      center: new kakao.maps.LatLng(lat, lng),
      level: 4
    })
    placesService = new kakao.maps.services.Places(kakaoMap)
    markers.forEach(m => m.setMap(null))
    markers = []
  })
}

/** 컴포넌트 마운트 */
onMounted(async () => {
  await loadRegions()
  await loadKakaoMapSdk()
  let lat = 37.5665, lng = 126.9780
  try {
    const res = await fetch('http://127.0.0.1:8000/map/', { method: 'POST' })
    const data = await res.json()
    lat = data.lat; lng = data.lng
  } catch {}
  initMap(lat, lng)
})

/** 검색 및 마커 생성 */
function onSearch() {
  if (!selectedBank.value || !placesService) return
  const keyword = [selectedSido.value, selectedGugun.value, selectedBank.value].join(' ')
  kakao.maps.load(() => {
    placesService.keywordSearch(keyword, (result, status) => {
      if (status === kakao.maps.services.Status.OK) {
        banks.value = result.map(i => ({ name: i.place_name, lat: +i.y, lng: +i.x }))
        placeMarkers()
      } else {
        console.error('검색 실패:', status)
      }
    })
  })
}

/** 마커 표시 및 제거 */
function placeMarkers() {
  if (!kakaoMap || banks.value.length === 0) return
  markers.forEach(m => m.setMap(null))
  markers = []

  const bounds = new kakao.maps.LatLngBounds()
  banks.value.forEach(b => {
    const pos = new kakao.maps.LatLng(b.lat, b.lng)
    const marker = new kakao.maps.Marker({ map: kakaoMap, position: pos, title: b.name })
    markers.push(marker)
    bounds.extend(pos)
  })
  kakaoMap.setBounds(bounds)
}
</script>

<style scoped>
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
.map-container {
  width: 100%;
  height: 400px;
  border: 1px solid #ddd;
}


</style>
