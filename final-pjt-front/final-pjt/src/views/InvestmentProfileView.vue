<template>
  <v-container fluid>
    <!-- 네비게이션 바 -->
    <v-row>
      <v-col cols="12">
        <NavigationBar />
      </v-col>
    </v-row>

    <v-row justify="center">
      <v-col cols="12" lg="10" xl="8">
        <!-- 프로필 헤더 -->
        <div class="text-center mb-8">
          <h1 class="text-h3 font-weight-bold mb-2">나의 투자 프로필</h1>
          <p class="text-subtitle-1 text-grey-darken-1">
            투자 성향과 목표를 한눈에 확인하세요
          </p>
        </div>

        <!-- 로딩 상태 -->
        <div v-if="loading" class="d-flex align-center justify-center">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
          />
          <span class="ml-4 text-h6">프로필 정보를 불러오는 중...</span>
        </div>

        <!-- 에러 상태 -->
        <v-alert
          v-else-if="error"
          type="error"
          variant="tonal"
          class="mb-6"
        >
          <template v-slot:prepend>
            <v-icon icon="mdi-alert-circle" />
          </template>
          {{ error }}
          <template v-slot:append>
            <v-btn
              color="error"
              variant="text"
              @click="fetchStatus"
            >
              다시 시도
            </v-btn>
          </template>
        </v-alert>

        <!-- 프로필 컨텐츠 -->
        <div v-else>
          <v-row>
            <!-- 투자 성향 분석 카드 -->
            <v-col cols="12" md="6">
              <v-card elevation="2" class="h-100">
                <v-img
                  src="@/assets/images/investment-analysis.jpg"
                  height="200"
                  cover
                  class="align-end"
                >
                  <v-card-title class="text-white text-shadow">
                    투자 성향 분석
                  </v-card-title>
                </v-img>
                <v-card-text class="d-flex flex-column h-100">
                  <div class="flex-grow-1">
                    <p class="text-body-1 mb-4">
                      나의 투자 성향을 분석하고<br>
                      맞춤형 투자 전략을 확인하세요
                    </p>
                  </div>
                  <v-btn
                    block
                    color="primary"
                    variant="elevated"
                    class="mt-auto"
                    @click="goToSurvey"
                  >
                    <v-icon icon="mdi-chart-line" class="mr-2" />
                    투자 성향 분석하기
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- 자산 목표 설정 카드 -->
            <v-col cols="12" md="6">
              <v-card elevation="2" class="h-100">
                <v-img
                  src="@/assets/images/investment-goal.jpg"
                  height="200"
                  cover
                  class="align-end"
                >
                  <v-card-title class="text-white text-shadow">
                    자산 목표 설정
                  </v-card-title>
                </v-img>
                <v-card-text class="d-flex flex-column h-100">
                  <div class="flex-grow-1">
                    <div v-if="goalProgress">
                      <!-- 진행률 게이지 -->
                      <div class="d-flex justify-center mb-6">
                        <v-progress-circular
                          :model-value="goalProgress.progress_percentage"
                          :color="getProgressColor(goalProgress.progress_percentage)"
                          size="120"
                          width="12"
                        >
                          {{ goalProgress.progress_percentage }}%
                        </v-progress-circular>
                      </div>

                      <!-- 자산 정보 -->
                      <v-list>
                        <v-list-item>
                          <template v-slot:prepend>
                            <v-icon icon="mdi-wallet" color="primary" />
                          </template>
                          <v-list-item-title>현재 자산</v-list-item-title>
                          <v-list-item-subtitle>
                            {{ formatCurrency(goalProgress.current_asset) }} 만원
                          </v-list-item-subtitle>
                        </v-list-item>

                        <v-list-item>
                          <template v-slot:prepend>
                            <v-icon icon="mdi-target" color="primary" />
                          </template>
                          <v-list-item-title>목표 자산</v-list-item-title>
                          <v-list-item-subtitle>
                            {{ formatCurrency(goalProgress.target_asset) }} 만원
                          </v-list-item-subtitle>
                        </v-list-item>

                        <v-list-item>
                          <template v-slot:prepend>
                            <v-icon icon="mdi-chart-timeline-variant" color="primary" />
                          </template>
                          <v-list-item-title>달성률</v-list-item-title>
                          <v-list-item-subtitle>
                            {{ goalProgress.progress_percentage }}%
                          </v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </div>
                  </div>
                  <v-btn
                    block
                    color="primary"
                    variant="elevated"
                    class="mt-auto"
                    @click="goToGoal"
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
              color="primary"
              size="x-large"
              variant="elevated"
              @click="goToRecommendations"
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
import axios from 'axios'

const router = useRouter()
const profile = ref(null)
const goal = ref(null)
const goalProgress = ref(null)
const error = ref(null)
const loading = ref(true)

async function fetchStatus() {
  try {
    const statusRes = await axios.get('/investment-profile/status/')
    const { has_investment_goal } = statusRes.data

    const profileRes = await axios.get('/investment-profile/profile/')
    profile.value = profileRes.data

    if (has_investment_goal) {
      const goalProgressRes = await axios.get('/investment-profile/goal/progress/')
      goalProgress.value = goalProgressRes.data
      goal.value = {
        expected_annual_return: goalProgressRes.data.expected_annual_return || 0
      }
    }
  } catch (err) {
    error.value = '데이터 로딩 중 오류 발생'
    console.error(err)
  } finally {
    loading.value = false
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
  if (percentage >= 50) return 'primary'
  if (percentage >= 30) return 'warning'
  return 'error'
}

onMounted(fetchStatus)
</script>

<style scoped>
.text-shadow {
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.h-100 {
  height: 100%;
}

.flex-grow-1 {
  flex-grow: 1;
}

.mt-auto {
  margin-top: auto;
}
</style>
