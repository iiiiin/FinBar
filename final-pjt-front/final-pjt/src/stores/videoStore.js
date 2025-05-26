// stores/videoStore.js
import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export const useVideoStore = defineStore('video', () => {
  const videos = ref([]) 
  const lastQuery = ref('')
  return { videos, lastQuery }
})
