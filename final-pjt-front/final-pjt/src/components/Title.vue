<template>
  <v-row class="title-row" align="center">
    <v-col cols="12">
      <h2 class="title-text">{{ title }}</h2>
      <v-divider class="mt-2"></v-divider>
    </v-col>
  </v-row>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.title-row {
  margin-top: 16px;
  margin-bottom: 16px;
}
.title-text {
  font-size: 24px;
  font-weight: 500;
}
</style>
