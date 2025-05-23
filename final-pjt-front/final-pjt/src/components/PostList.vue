<template>
  <v-list two-line>
    <template v-for="(post, index) in posts" :key="index">
      <v-list-item class="post-item" @click="onSelect(post)">
        <!-- <v-list-item-content> -->
          <v-list-item-title>{{ post.title }}</v-list-item-title>
          <v-list-item-subtitle>
            작성자: {{ post.nickname }} 
          </v-list-item-subtitle>
          <v-list-item-subtitle>
            작성일시: {{ formatDate(post.created_at || post.createdAt) }}
          </v-list-item-subtitle>
        <!-- </v-list-item-content> -->
      </v-list-item>
      <v-divider inset v-if="index < posts.length - 1" />
    </template>
  </v-list>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  posts: {
    type: Array,
    default: () => []
  }
})
const emits = defineEmits(['select'])

function onSelect(id) {
  emits('select', id)
}

function formatDate(date) {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString()
}
</script>

<style scoped>
.post-item {
  cursor: pointer;
}
</style>