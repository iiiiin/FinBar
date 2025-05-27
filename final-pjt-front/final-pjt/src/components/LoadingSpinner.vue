<template>
  <div class="loading-images">
    <img
      :src="images[currentIndex]"
      alt="로딩 중"
      class="loading-img"
    />
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    images: {
      type: Array,
      required: true,
    },
    interval: {
      type: Number,
      default: 500,
    },
  },
  data() {
    return {
      currentIndex: 0,
      timer: null,
    };
  },
  mounted() {
    this.timer = setInterval(() => {
      this.currentIndex = (this.currentIndex + 1) % this.images.length;
    }, this.interval);
  },
  beforeUnmount() {
    clearInterval(this.timer);
  },
};
</script>

<style scoped>
.loading-images {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
.loading-img {
  width: 120px;
  height: auto;
}
</style>
