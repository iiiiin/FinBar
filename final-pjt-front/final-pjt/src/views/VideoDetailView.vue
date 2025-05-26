<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <v-row class="my-4">
      <v-col cols="12">
        <v-btn text @click="goBack">← 돌아가기</v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <div class="video-wrapper">
          <iframe
            :src="`https://www.youtube.com/embed/${videoId}`"
            frameborder="0"
            allowfullscreen
            width="100%"
            height="400"
          ></iframe>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const videoId = route.params.id

function goBack() {
  router.back()
}
</script>

<style scoped>
.video-wrapper {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 */
  height: 0;
  overflow: hidden;
}
.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
