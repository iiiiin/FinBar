<template>
  <v-container fluid class="pa-0">
    <!-- 네비게이션 바 -->
    <NavigationBar />

    <!-- 12컬럼: 2 + 4 + 4 + 2 -->
    <v-row no-gutters>
      <!-- 빈 2칸 -->
      <v-col cols="2"></v-col>

      <!-- 가운데 왼쪽 4칸: 기존 이미지 -->
      <v-col cols="4" class="d-flex align-center justify-center">
        <v-img
          :src="images[1]"
          contain
          max-width="80%"
          max-height="80%"
          height="700"
        />
      </v-col>

      <!-- 가운데 오른쪽 4칸: 캐러셀 -->
      <v-col cols="4" class="position-relative">
        <div class="menu-background">
          <v-carousel
            cycle
            :interval="3000"
            hide-delimiter-background
            class="menu-carousel"
          >
            <v-carousel-item
              v-for="(slide, i) in slides"
              :key="i"
            >
              <router-link :to="{ name: slide.link }" class="carousel-link">
                <v-row
                  class="fill-height d-flex flex-column slide-content"
                  align="center"
                  justify="center"
                >
                  <!-- 이미지 반쪽 -->
                  <v-col
                    class="d-flex align-center justify-center image-col"
                    style="flex: 0.4;"
                  >
                    <img :src="slide.image" alt="" class="slide-image" />
                  </v-col>
                  <!-- 텍스트 반쪽 -->
                  <v-col
                    class="d-flex flex-column align-center justify-center text-col"
                    style="flex: 0.6;"
                  >
                    <h2 class="text-h4 mb-1">{{ slide.title }}</h2>
                    <p class="text-body-1">{{ slide.description }}</p>
                  </v-col>
                </v-row>
              </router-link>
            </v-carousel-item>
          </v-carousel>
        </div>
      </v-col>

      <!-- 빈 2칸 -->
      <v-col cols="2"></v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import NavigationBar from '@/components/NavigationBar.vue'
import { ref } from 'vue'

// 기존 이미지 배열
const images = ref([
  '/images/cup.png',
  '/images/welcome.png',
  '/images/home3.png',
])

// 캐러셀에 들어갈 슬라이드 정보
const slides = ref([
  {
    image: '/images/balance.png',
    title: '금융 상품 비교',
    description: '나에게 맞는 금융 상품을 비교해보세요.',
    link: 'productList'
  },
  {
    image: '/images/gold.png',
    title: '현물 상품 가격 변동',
    description: '금/은 현물의 시세 추이를 확인해보세요.',
    link: 'spotPrice'
  },
  {
    image: '/images/finder.png',
    title: '관심 종목 정보 검색',
    description: '관심 주식에 대한 정보를 검색해보세요.',
    link: 'videoStock'
  },
  {
    image: '/images/bank.png',
    title: '은행 위치 검색',
    description: '주변 은행 위치를 찾아보세요.',
    link: 'bankMap'
  }
])
</script>

<style scoped>
.menu-background {
  position: relative;
  width: 100%;
  height: 650px;
  background-image: url('/images/menu.png');
  background-repeat: no-repeat;
  background-position: center center;
  background-size: contain;
  margin-top: 64px;
}

.menu-carousel {
  position: absolute;
  top: 55%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 60%;
}

.slide-content {
  transform: scale(0.7);
  transform-origin: center center;
}

.image-col {
  margin-top: 10%;
}

.slide-image {
  max-height: 180px;
  width: auto;
  object-fit: contain;
}

.text-col h2 {
  margin-bottom: 4px;
}

::v-deep .carousel-link,
::v-deep .carousel-link:hover,
::v-deep .carousel-link:focus,
::v-deep .carousel-link *,
::v-deep .carousel-link *:hover {
  color: inherit !important;
  text-decoration: none !important;
}
</style>
