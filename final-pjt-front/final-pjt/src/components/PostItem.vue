<template>
  <div class="post-item" @click="$emit('click')">
    <h3>{{ post.title }}</h3>
    <div class="meta">
      <span>작성자: {{ post.author }}</span>
      <span>{{ new Date(post.createdAt).toLocaleDateString() }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ post: Object })
defineEmits(['click'])
</script>
