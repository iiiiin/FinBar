<template>
  <v-app>
    <v-main>
      <v-container fluid fill-height class="error-page">
        <v-row align="center" justify="center">
          <v-col cols="12" md="8" class="text-center">
            <v-fade-transition mode="in-out">
              <!-- <v-icon large class="error-icon">mdi-cloud-alert</v-icon> -->
            </v-fade-transition>
            <v-slide-y-transition mode="in-out">
              <h1 class="error-code">!</h1>
            </v-slide-y-transition>
            <v-scale-transition>
              <h2 class="error-message">페이지를 찾을 수 없어요</h2>
            </v-scale-transition>
            <p class="error-description">죄송합니다. 요청하신 페이지가 존재하지 않습니다.</p>
            <v-btn color="blue lighten-1" large to="/" class="home-btn">
              <v-icon left>mdi-home</v-icon> 홈으로 이동
            </v-btn>
          </v-col>
        </v-row>
        <!-- Animated shapes -->
        <div class="shape circle1"></div>
        <div class="shape circle2"></div>
        <div class="shape triangle"></div>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'Error404Page',
};
</script>

<style scoped>
.error-page {
  position: relative;
  background: linear-gradient(135deg, #2196f3, #21cbf3);
  color: white;
  overflow: hidden;
}
.error-icon {
  font-size: 5rem;
  animation: float 3s ease-in-out infinite;
}
.error-code {
  font-size: 6rem;
  margin: 0.5rem 0;
  font-weight: bold;
  animation: bounce 2s infinite;
}
.error-message {
  font-size: 2rem;
  margin-bottom: 1rem;
  animation: fadeIn 2s ease-in-out;
}
.error-description {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}
.home-btn {
  animation: pulse 2s infinite;
}
.shape {
  position: absolute;
  opacity: 0.3;
}
.circle1 {
  width: 150px;
  height: 150px;
  background-color: #ffffff;
  border-radius: 50%;
  top: 10%;
  left: 5%;
  animation: float 6s ease-in-out infinite;
}
.circle2 {
  width: 200px;
  height: 200px;
  background-color: #ffffff;
  border-radius: 50%;
  bottom: 15%;
  right: 10%;
  animation: float 5s ease-in-out infinite;
}
.triangle {
  width: 0;
  height: 0;
  border-left: 75px solid transparent;
  border-right: 75px solid transparent;
  border-bottom: 130px solid #ffffff;
  top: 50%;
  right: 30%;
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-25px); }
  60% { transform: translateY(-15px); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
</style>