<template>
  <v-container fluid class="pa-0">
    <NavigationBar />
    <!-- 2분할 Lottie 캐러셀 -->
    <v-carousel
      height="350"
      cycle
      :interval="3000"
      hide-delimiter-background
    >
      <v-carousel-item
        v-for="(slide, i) in slides"
        :key="i"
      >
        <v-row class="fill-height">
          <!-- 왼쪽 50%: Lottie -->
          <v-col cols="12" md="6" class="pa-0">
            <Lottie
              :animation-link="slide.anim"
              :loop="true"
              :autoplay="true"
              :width="300"
              :height="400"
            />
          </v-col>

          <!-- 오른쪽 50%: 텍스트 -->
          <v-col
            cols="12"
            md="6"
            class="d-flex flex-column align-center justify-center pa-6"
          >
            <h2 class="text-h4 mb-4">{{ slide.title }}</h2>
            <p class="text-body-1">{{ slide.description }}</p>
          </v-col>
        </v-row>
      </v-carousel-item>
    </v-carousel>
    <!-- Lottie 캐러셀
    <v-carousel
      height="350"
      cycle
      :interval="3000"      
      hide-delimiter-background
    >
      <v-carousel-item
        v-for="(anim, i) in lionAnimations"
        :key="i"
      >
        <Lottie
          :animation-link="anim"
          :loop="true"
          :autoplay="true"
          style="width: 100%; height: 100%;"
        />
      </v-carousel-item>
    </v-carousel> -->

    <!-- 카드 영역: link 프로퍼티로 이동 -->
    <v-row class="my-8" justify="space-around">
      <v-col cols="12" sm="4" v-for="(card, idx) in cards" :key="idx">
        <v-card elevation="2">
          <v-img :src="card.img" height="160px" />
          <v-card-title>{{ card.title }}</v-card-title>
          <v-card-text>{{ card.desc }}</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import NavigationBar from '@/components/NavigationBar.vue'
import { ref } from 'vue'

// 슬라이드별 애니 + 텍스트 묶음
const slides = ref([
  {
    anim: 'https://lottie.host/2ded8851-57ef-4d48-a0c1-3f3f855c4704/tGgjpAKHcz.json',
    title: '예/적금 상품 비교',
    description: '나에게 맞는 금융 상품을 찾아 비교해보세요.'
  },
  {
    anim: 'https://lottie.host/adbad6b9-0129-4228-8d58-983884512b50/uGZToDlVbf.json',
    title: '현물 상품 가격 변동',
    description: '금/은 현물의 시세 변동 추이를 확인해보세요.'
  },
  {
    anim: 'https://lottie.host/75e710e5-6b7a-41fb-a6d0-b2133cce1590/axc220tXK3.json',
    title: '관심 종목 정보 검색',
    description: '관심 주식에 대한 영상 정보를 검색해보세요.'
  },
  {
    anim: 'https://lottie.host/a42a4bbc-ccdc-4b90-9adb-5ee0712c3742/en26Jf0zKh.json',
    title: '은행 위치 검색',
    description: '주변 은행 위치를 찾아보세요.'
  }
])

// 카드 데이터에 임의의 link(name) 추가
const cards = ref([
  {
    img: 'https://picsum.photos/seed/account/400/300',
    title: '예/적금 상품 비교',
    desc: '예금, 적금 상품 맞춤형 추천',
    link: 'home'       // 가정한 라우트 이름
  },
  {
    img: 'https://picsum.photos/seed/transfer/400/300',
    title: '현물 상품 가격 변동',
    desc: '금, 은 시세 변동 추이 그래프',
    cta: '이체 화면으로',
    link: 'home'       // 가정한 라우트 이름
  },
  {
    img: 'https://picsum.photos/seed/report/400/300',
    title: '관심 종목 정보 검색',
    desc: '주식 종목 Youtube 영상 검색',
    link: 'home'        // 가정한 라우트 이름
  },
])
</script>

<style scoped>
.lottie-wrapper {
  display: block;
  cursor: pointer;
  overflow: hidden;
}
</style>
