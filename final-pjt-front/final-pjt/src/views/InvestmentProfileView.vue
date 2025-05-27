<template>
  <v-container fluid class="profile-container">
    <!-- 네비게이션 바 -->
    <v-row>
      <v-col cols="12">
        <NavigationBar />
      </v-col>
    </v-row>

    <v-row justify="center" class="mt-4">
      <v-col cols="12" lg="10" xl="8">
        <!-- 프로필 헤더 -->
        <div class="text-center mb-8 profile-header">
          <h1 class="text-h3 font-weight-bold mb-2">나의 투자 프로필</h1>
          <p class="text-subtitle-1 text-grey-darken-1">
            투자 성향과 목표를 한눈에 확인하세요
          </p>
        </div>

        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-container">
          <LoadingSpinner
            v-if="loading"
            :images="loadingImages"
            :interval="100"
          />
          <span class="text-h6">프로필 정보를 불러오는 중...</span>
        </div>

        <!-- 에러 상태 -->
        <v-alert
          v-else-if="error"
          type="error"
          variant="tonal"
          class="mb-6 error-alert"
          elevation="2"
        >
          <template v-slot:prepend>
            <v-icon icon="mdi-alert-circle" size="large" />
          </template>
          <div class="d-flex align-center">
            <span class="text-body-1">{{ error }}</span>
            <v-spacer />
            <v-btn
              color="error"
              variant="text"
              @click="fetchStatus"
              class="ml-4"
            >
              다시 시도
            </v-btn>
          </div>
        </v-alert>

        <!-- 프로필 컨텐츠 -->
        <div v-else class="profile-content">
          <v-row>
            <!-- 투자 성향 분석 카드 -->
            <v-col cols="12" md="6" class="mb-4">
              <v-card elevation="2" class="h-100 profile-card" :class="{ 'card-hover': true }">
                <v-img
                  src="@/assets/images/investment-analysis.jpg"
                  height="200"
                  cover
                  class="align-end card-image"
                  gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.8)"
                >
                  <v-card-title class="text-white text-shadow">
                    투자 성향 분석
                  </v-card-title>
                </v-img>
                <v-card-text class="d-flex flex-column h-100 pa-6">
                  <v-carousel hide-delimiter-background height="220">
                    <!-- 1. 투자 성향이란? -->
                    <v-carousel-item>
                      <div class="pa-4 carousel-text">
                        <b>투자 성향이란?</b><br>
                        투자 성향은 본인의 위험 선호도, 투자 기간, 투자 목적 등을 종합적으로 분석하여<br>
                        <b>안정형, 위험중립형, 적극형</b> 등으로 분류합니다.<br>
                        <br>
                        분석 결과에 따라 적합한 금융 상품과 투자 전략을 추천받을 수 있습니다.
                      </div>
                    </v-carousel-item>
                    <!-- 2. 안정형 추천 -->
                    <v-carousel-item>
                      <div class="pa-4 carousel-text">
                        <b>안정형 투자자 추천 상품</b><br>
                        <ul>
                          <li>예금, 적금</li>
                          <li>국공채, MMF</li>
                          <li>저위험 채권형 펀드</li>
                        </ul>
                        <span class="text-caption text-grey">원금 손실을 최소화하고자 하는 투자자에게 적합</span>
                      </div>
                    </v-carousel-item>
                    <!-- 3. 위험중립형 추천 -->
                    <v-carousel-item>
                      <div class="pa-4 carousel-text">
                        <b>위험중립형 투자자 추천 상품</b><br>
                        <ul>
                          <li>혼합형 펀드</li>
                          <li>우량주 주식</li>
                          <li>중위험 채권</li>
                        </ul>
                        <span class="text-caption text-grey">적당한 위험과 수익을 추구하는 투자자에게 적합</span>
                      </div>
                    </v-carousel-item>
                    <!-- 4. 적극형 추천 -->
                    <v-carousel-item>
                      <div class="pa-4 carousel-text">
                        <b>적극형 투자자 추천 상품</b><br>
                        <ul>
                          <li>주식, ETF</li>
                          <li>해외펀드, 대체투자</li>
                          <li>고수익 성장주</li>
                        </ul>
                        <span class="text-caption text-grey">높은 수익을 위해 위험을 감수할 수 있는 투자자에게 적합</span>
                      </div>
                    </v-carousel-item>
                  </v-carousel>
                  <v-btn
                    block
                    color="grey darken-3"
                    variant="elevated"
                    class="mt-4 action-button"
                    @click="goToSurvey"
                    elevation="2"
                    size="small"
                  >
                    <v-icon icon="mdi-chart-line" class="mr-2" />
                    투자 성향 분석하기
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- 자산 목표 설정 카드 -->
            <v-col cols="12" md="6" class="mb-4">
              <v-card elevation="2" class="h-100 profile-card" :class="{ 'card-hover': true }">
                <v-img
                  src="@/assets/images/investment-goal.jpg"
                  height="200"
                  cover
                  class="align-end card-image"
                  gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.8)"
                >
                  <v-card-title class="text-white text-shadow">
                    자산 목표 설정
                  </v-card-title>
                </v-img>
                <v-card-text class="d-flex flex-column h-100 pa-6">
                  <div class="flex-grow-1">
                    <div v-if="goalProgress" class="goal-progress">
                      <!-- 진행률 게이지 -->
                      <div class="d-flex justify-center mb-6">
                        <v-progress-circular
                          :model-value="goalProgress.progress_percentage"
                          :color="getProgressColor(goalProgress.progress_percentage)"
                          size="120"
                          width="12"
                          class="progress-gauge"
                        >
                          <span class="text-h5 font-weight-bold">
                            {{ goalProgress.progress_percentage }}%
                          </span>
                        </v-progress-circular>
                      </div>

                      <!-- 자산 정보 -->
                      <v-list class="asset-list">
                        <v-list-item class="asset-item">
                          <template v-slot:prepend>
                            <v-icon icon="mdi-wallet" color="grey darken-3" size="large" />
                          </template>
                          <v-list-item-title class="text-subtitle-1 font-weight-bold">
                            현재 자산
                          </v-list-item-title>
                          <v-list-item-subtitle class="text-h6 mt-1">
                            {{ formatCurrency(goalProgress.current_asset) }} 만원
                          </v-list-item-subtitle>
                        </v-list-item>

                        <v-list-item class="asset-item">
                          <template v-slot:prepend>
                            <v-icon icon="mdi-target" color="grey darken-3" size="large" />
                          </template>
                          <v-list-item-title class="text-subtitle-1 font-weight-bold">
                            목표 자산
                          </v-list-item-title>
                          <v-list-item-subtitle class="text-h6 mt-1">
                            {{ formatCurrency(goalProgress.target_asset) }} 만원
                          </v-list-item-subtitle>
                        </v-list-item>

                        <v-list-item class="asset-item">
                          <template v-slot:prepend>
                            <v-icon icon="mdi-chart-timeline-variant" color="grey darken-3" size="large" />
                          </template>
                          <v-list-item-title class="text-subtitle-1 font-weight-bold">
                            달성률
                          </v-list-item-title>
                          <v-list-item-subtitle class="text-h6 mt-1">
                            {{ goalProgress.progress_percentage }}%
                          </v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </div>
                  </div>
                  <v-btn
                    block
                    color="grey darken-3"
                    variant="elevated"
                    class="mt-auto action-button"
                    @click="goToGoal"
                    elevation="2"
                  >
                    <v-icon icon="mdi-pencil" class="mr-2" />
                    목표 설정하기
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- 추천 버튼 -->
          <div class="text-center mt-8">
            <v-btn
              color="grey darken-3"
              size="x-large"
              variant="elevated"
              @click="goToRecommendations"
              class="recommendation-button"
              elevation="3"
            >
              <v-icon icon="mdi-lightbulb" class="mr-2" />
              맞춤 추천 보러가기
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/NavigationBar.vue'
import { investmentAPI } from '@/services/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const router = useRouter()
const profile = ref(null)
const goal = ref(null)
const goalProgress = ref(null)
const error = ref(null)
const loading = ref(true)
const loadingImages = ['images/shaker1.png','images/shaker2.png']

async function fetchStatus() {
  try {
    const statusRes = await investmentAPI.checkStatus();
    const { has_investment_goal } = statusRes.data;

    const profileRes = await investmentAPI.getProfile();
    profile.value = profileRes.data;

    if (has_investment_goal) {
      const goalProgressRes = await investmentAPI.getGoalProgress();
      goalProgress.value = goalProgressRes.data;
      goal.value = {
        expected_annual_return: goalProgressRes.data.expected_annual_return || 0
      }
    }
  } catch (err) {
    error.value = '데이터 로딩 중 오류 발생';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

function goToRecommendations() {
  if (profile.value && goal.value) {
    router.push({ name: 'recommendations' })
  } else {
    error.value = '추천을 보기 위해선 투자 프로필과 목표가 필요합니다.'
  }
}

function goToSurvey() {
  router.push({ name: 'survey' })
}

function goToGoal() {
  router.push({ name: 'investmentGoal' })
}

// 통화 포맷 함수
function formatCurrency(value) {
  return new Intl.NumberFormat('ko-KR').format(value)
}

// 진행률에 따른 색상 반환 함수
function getProgressColor(percentage) {
  if (percentage >= 80) return 'success'
  if (percentage >= 50) return 'grey darken-3'
  if (percentage >= 30) return 'warning'
  return 'error'
}

onMounted(fetchStatus)
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 4rem;
}

.profile-header {
  margin-top: 2rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.error-alert {
  border-radius: 12px;
}

.profile-content {
  animation: fadeIn 0.5s ease-in-out;
}

.profile-card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-image {
  position: relative;
}

.text-shadow {
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.action-button {
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.progress-gauge {
  transition: all 0.3s ease;
}

.asset-list {
  background: transparent;
}

.asset-item {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  background-color: rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;
}

.asset-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.recommendation-button {
  transition: all 0.3s ease;
  padding: 1rem 2rem;
}

.recommendation-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .profile-header {
    margin-top: 1rem;
  }

  .text-h3 {
    font-size: 2rem !important;
  }
}

@media (max-width: 600px) {
  .profile-container {
    padding: 1rem;
  }

  .text-h3 {
    font-size: 1.75rem !important;
  }

  .profile-card {
    margin-bottom: 1rem;
  }

  .asset-item {
    padding: 0.75rem;
  }
}

.carousel-text {
  font-size: 1.15rem;
  line-height: 1.7;
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.action-button {
  font-size: 0.95rem !important;
  padding: 0.5rem 1.2rem !important;
  min-height: 36px !important;
  max-width: 220px;
  margin-left: auto;
  margin-right: auto;
}
</style>
