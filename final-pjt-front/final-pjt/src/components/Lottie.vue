<!-- src/components/Lottie.vue -->
<template>
  <div ref="container" class="lottie-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import lottie from 'lottie-web'

const props = defineProps({
  animationLink: {
    type: String,
    required: true
  },
  width: {
    type: Number,
    default: 100
  },
  height: {
    type: Number,
    default: 100
  },
  loop: {
    type: Boolean,
    default: true
  },
  autoplay: {
    type: Boolean,
    default: true
  }
})

const container = ref(null)
let animation = null

async function loadAnimation() {
  if (!container.value) return

  try {
    const response = await fetch(props.animationLink)
    const animationData = await response.json()

    if (animation) {
      animation.destroy()
    }

    animation = lottie.loadAnimation({
      container: container.value,
      renderer: 'svg',
      loop: props.loop,
      autoplay: props.autoplay,
      animationData
    })
  } catch (error) {
    console.error('Failed to load Lottie animation:', error)
  }
}

watch(() => props.animationLink, loadAnimation)

onMounted(loadAnimation)

onBeforeUnmount(() => {
  if (animation) {
    animation.destroy()
  }
})
</script>

<style scoped>
.lottie-container {
  display: inline-flex;
  justify-content: center;
  align-items: center;
}
</style> 