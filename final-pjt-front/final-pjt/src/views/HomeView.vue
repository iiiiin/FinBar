<template>
  <v-container fluid class="pa-0">
    <NavigationBar />

    <!-- 메뉴판 배경 -->
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
          <!-- 상하 2분할: flex 비율 조정 -->
          <v-row
            class="fill-height d-flex flex-column"
            align="center"
            justify="center"
          >
            <!-- 이미지 영역 -->
            <v-col
              class="d-flex align-center justify-center image-col"
              style="flex: 0.4;"
            >
              <img :src="slide.image" alt="" class="slide-image" />
            </v-col>

            <!-- 텍스트 영역 -->
            <v-col
              class="d-flex flex-column align-center justify-center text-center text-col"
              style="flex: 0.6;"
            >
              <h2 class="text-h4 mb-1">{{ slide.title }}</h2>
              <p class="text-body-1">{{ slide.description }}</p>
            </v-col>
          </v-row>
        </v-carousel-item>
      </v-carousel>
    </div>
  </v-container>
</template>

<script setup>
import NavigationBar from '@/components/NavigationBar.vue'
import { ref } from 'vue'

const slides = ref([
  {
    image: '/images/money_fueru_dollar.png',
    title: '예/적금 상품 비교',
    description: '나에게 맞는 금융 상품을 찾아 비교해보세요.'
  },
  {
    image: '/images/money_fueru_dollar.png',
    title: '현물 상품 가격 변동',
    description: '금/은 현물의 시세 변동 추이를 확인해보세요.'
  },
  {
    image: '/images/money_fueru_dollar.png',
    title: '관심 종목 정보 검색',
    description: '관심 주식에 대한 영상 정보를 검색해보세요.'
  },
  {
    image: '/images/money_fueru_dollar.png',
    title: '은행 위치 검색',
    description: '주변 은행 위치를 찾아보세요.'
  }
])
</script>

<style scoped>
.menu-background {
  position: relative;
  width: 100%;
  height: 650px;
  margin-top: 64px;
  background-image: url('/images/menu.png');
  background-repeat: no-repeat;
  background-position: center center;
  background-size: contain;
}

.menu-carousel {
  position: absolute;
  /* 아래로 조금 더 내리기 */
  top: 55%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 45%;   /* 약간 축소 */
  height: 60%;  /* 약간 축소 */
}

/* 이미지 영역을 아래로 조금 내림 */
.image-col {
  margin-top: 10%;
}

/* 이미지 크기 제한 */
.slide-image {
  max-height: 180px;
  width: auto;
  object-fit: contain;
}

/* 제목-본문 간격 줄이기 */
.text-col h2 {
  margin-bottom: 4px;
}
</style>
