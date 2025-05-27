<template>
  <v-container fluid class="pa-0">
    <div>
    <NavigationBar />
    </div>

    <v-row no-gutters>
      <!-- 왼쪽 6칸: 사진 3장이 연속적으로 반복될 애니메이션 공간 -->
      <v-col cols="6" class="d-flex align-center justify-center">
        <v-img
          :src="images[0]"
          contain
          max-width="80%"
          max-height="80%"
          height="700"
        />
      </v-col>

      <!-- 중간 3칸: 텍스트 공간 -->
      <v-col cols="3" class="d-flex align-center justify-center">
        <div class="text-space">
          나만을 위한 투자레시피!  <br>
          체리를 눌러 시작해보세요 ▶️
        </div>
      </v-col>

      <v-col cols="3" class="d-flex align-center justify-center">
        <RouterLink :to="{ name : 'menu'}">
          <v-img
            src="/images/cherry.png"
            alt="메뉴"
            width="100"
            height="100"
          />
        </RouterLink>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import NavigationBar from '@/components/NavigationBar.vue'
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

// 반복될 이미지 URL 배열
const images = ref([
  '/images/cup.png',
  '/images/home2.png',
  '/images/home3.png',
])
</script>

<style scoped>
.text-space {
  font-size: 1.25rem;
  text-align: center;
  padding: 0 16px;
}
</style>
