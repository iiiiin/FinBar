<template>
    <div class="plate-footer">
      <img :src="src" :alt="alt" class="plate-img" />
    </div>
  </template>
  
  <script setup>
  defineProps({
    /** 그림 파일 경로 (`/images/...`) */
    src: {
      type: String,
      required: true
    },
    /** 대체 텍스트 */
    alt: {
      type: String,
      default: 'footer image'
    }
  })
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
  </style>
  