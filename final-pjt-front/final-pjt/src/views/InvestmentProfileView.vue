<!-- src/views/InvestmentProfileView.vue -->
<template>
  <v-container fluid class="mt-8">
    <NavigationBar />

    <v-row justify="center">
      <v-col cols="12" lg="10" xl="8">
        <!-- 헤더 섹션 -->
        <div class="text-center mb-6">
          <h1 class="text-h3 font-weight-bold mb-2">투자 프로필</h1>
          <p class="text-subtitle-1 text-grey-darken-1">나만의 투자 전략을 수립하세요</p>
        </div>

        <!-- 프로필 상태 카드 -->
        <v-card elevation="3" class="mb-6 rounded-lg">
          <v-card-title class="text-h5 py-4 px-6 bg-primary text-white">
            <v-icon class="mr-3">mdi-account-check</v-icon>
            프로필 완성도
          </v-card-title>

          <!-- 로딩 상태 -->
          <v-card-text v-if="loading" class="text-center py-8">
            <v-progress-circular indeterminate color="primary" size="64" />
            <p class="mt-4 text-subtitle-1">프로필 정보를 불러오는 중...</p>
          </v-card-text>

          <!-- 에러 상태 -->
          <v-card-text v-else-if="error" class="pa-6">
            <v-alert type="error" variant="tonal">
              <v-alert-title>오류 발생</v-alert-title>
              {{ error }}
            </v-alert>
          </v-card-text>

          <!-- 프로필 상태 표시 -->
          <v-card-text v-else class="pa-6">
            <v-row>
              <v-col cols="12" md="6">
                <v-card 
                  :color="profileStatus.investment_profile ? 'success' : 'grey-lighten-3'"
                  :variant="profileStatus.investment_profile ? 'tonal' : 'outlined'"
                  class="pa-4 h-100"
                >
                  <div class="d-flex align-center mb-3">
                    <v-icon 
                      size="32"
                      :color="profileStatus.investment_profile ? 'success' : 'grey'"
                    >
                      {{ profileStatus.investment_profile ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                    </v-icon>
                    <h3 class="ml-3">투자 성향 분석</h3>
                  </div>
                  <p class="text-body-2 mb-0">
                    {{ profileStatus.investment_profile 
                      ? '투자 성향 분석이 완료되었습니다.' 
                      : '설문을 통해 나의 투자 성향을 파악하세요.' }}
                  </p>
                  <v-chip 
                    v-if="profileData?.investment_profile?.risk_type"
                    class="mt-3"
                    color="success"
                    variant="elevated"
                  >
                    {{ profileData.investment_profile.risk_type }}
                  </v-chip>
                </v-card>
              </v-col>

              <v-col cols="12" md="6">
                <v-card 
                  :color="profileStatus.investment_goal ? 'success' : 'grey-lighten-3'"
                  :variant="profileStatus.investment_goal ? 'tonal' : 'outlined'"
                  class="pa-4 h-100"
                >
                  <div class="d-flex align-center mb-3">
                    <v-icon 
                      size="32"
                      :color="profileStatus.investment_goal ? 'success' : 'grey'"
                    >
                      {{ profileStatus.investment_goal ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                    </v-icon>
                    <h3 class="ml-3">투자 목표 설정</h3>
                  </div>
                  <p class="text-body-2 mb-0">
                    {{ profileStatus.investment_goal 
                      ? '투자 목표가 설정되었습니다.' 
                      : '달성하고 싶은 투자 목표를 설정하세요.' }}
                  </p>
                  <v-chip 
                    v-if="goalProgress?.achievement_status"
                    class="mt-3"
                    :color="getStatusColor(goalProgress.achievement_status)"
                    variant="elevated"
                  >
                    {{ goalProgress.achievement_status }}
                  </v-chip>
                </v-card>
              </v-col>
            </v-row>

            <!-- 진행률 표시 -->
            <v-progress-linear
              v-if="profileStatus.investment_profile || profileStatus.investment_goal"
              class="mt-6"
              :model-value="completionRate"
              color="primary"
              height="25"
              rounded
            >
              <template v-slot:default="{ value }">
                <strong>{{ Math.ceil(value) }}% 완료</strong>
              </template>
            </v-progress-linear>
          </v-card-text>

          <!-- 액션 버튼 -->
          <!-- src/views/InvestmentProfileView.vue -->

          <v-card-actions class="justify-center pa-6 bg-grey-lighten-5">
            <!-- 1. 투자 성향 분석 시작 -->
            <v-btn
              v-if="!profileStatus.investment_profile"
              color="primary"
              size="large"
              variant="elevated"
              @click="goToSurvey"
              prepend-icon="mdi-clipboard-text"
            >
              투자 성향 분석 시작
            </v-btn>

            <!-- 2. 투자 목표 설정하기 -->
            <v-btn
              v-else-if="!profileStatus.investment_goal"
              color="primary"
              size="large"
              variant="elevated"
              @click="goToGoalSetting"
              prepend-icon="mdi-target"
            >
              투자 목표 설정하기
            </v-btn>

            <!-- 3. 맞춤 추천 버튼 (▶ 항상 렌더, 완료된 경우에만 활성화) -->
            <v-btn
              color="success"
              size="large"
              variant="elevated"
              prepend-icon="mdi-lightbulb"
              :disabled="!profileStatus.investment_profile || !profileStatus.investment_goal || loading"
              @click="goToRecommendations"
            >
              맞춤 투자 상품 추천받기
            </v-btn>
          </v-card-actions>

        </v-card>

        <!-- 투자 목표 진행 상황 (목표가 있을 때만 표시) -->
        <v-card v-if="profileStatus.investment_goal && goalProgress" elevation="3" class="mb-6 rounded-lg">
          <v-card-title class="text-h5 py-4 px-6 bg-indigo text-white">
            <v-icon class="mr-3">mdi-trending-up</v-icon>
            투자 목표 달성 현황
          </v-card-title>
          
          <v-card-text class="pa-6">
            <v-row>
              <v-col cols="12" md="6">
                <div class="text-center">
                  <v-progress-circular
                    :model-value="goalProgress.progress_percentage"
                    :size="160"
                    :width="15"
                    :color="getProgressColor(goalProgress.progress_percentage)"
                  >
                    <div>
                      <div class="text-h4 font-weight-bold">{{ goalProgress.progress_percentage }}%</div>
                      <div class="text-caption">달성률</div>
                    </div>
                  </v-progress-circular>
                </div>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-list density="comfortable">
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="primary">mdi-cash</v-icon>
                    </template>
                    <v-list-item-title>현재 자산</v-list-item-title>
                    <v-list-item-subtitle>{{ formatCurrency(goalProgress.current_asset) }}만원</v-list-item-subtitle>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="success">mdi-flag-checkered</v-icon>
                    </template>
                    <v-list-item-title>목표 자산</v-list-item-title>
                    <v-list-item-subtitle>{{ formatCurrency(goalProgress.target_asset) }}만원</v-list-item-subtitle>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="orange">mdi-calendar-clock</v-icon>
                    </template>
                    <v-list-item-title>남은 기간</v-list-item-title>
                    <v-list-item-subtitle>{{ Math.floor(goalProgress.days_remaining / 365) }}년 {{ goalProgress.days_remaining % 365 }}일</v-list-item-subtitle>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="indigo">mdi-piggy-bank</v-icon>
                    </template>
                    <v-list-item-title>월 필요 저축액</v-list-item-title>
                    <v-list-item-subtitle>{{ formatCurrency(goalProgress.monthly_required_saving) }}만원</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>

            <v-divider class="my-4" />
            
            <div class="text-center">
              <v-btn
                color="primary"
                variant="outlined"
                @click="showUpdateAssetDialog = true"
                prepend-icon="mdi-update"
              >
                현재 자산 업데이트
              </v-btn>
            </div>
          </v-card-text>
        </v-card>

        <!-- 프로필 요약 정보 -->
        <v-card v-if="profileData && profileStatus.investment_profile && profileStatus.investment_goal" elevation="3" class="rounded-lg">
          <v-card-title class="text-h5 py-4 px-6 bg-teal text-white">
            <v-icon class="mr-3">mdi-account-details</v-icon>
            나의 투자 프로필 요약
          </v-card-title>
          
          <v-card-text class="pa-6">
            <v-row>
              <v-col cols="12" md="4">
                <v-card variant="outlined" class="pa-4 h-100">
                  <h4 class="text-h6 mb-3">기본 정보</h4>
                  <v-list density="compact">
                    <v-list-item>
                      <v-list-item-title>이름</v-list-item-title>
                      <v-list-item-subtitle>{{ profileData.nickname || profileData.username }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>나이</v-list-item-title>
                      <v-list-item-subtitle>{{ profileData.age }}세</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>이메일</v-list-item-title>
                      <v-list-item-subtitle>{{ profileData.email }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card>
              </v-col>

              <v-col cols="12" md="4">
                <v-card variant="outlined" class="pa-4 h-100">
                  <h4 class="text-h6 mb-3">투자 성향</h4>
                  <div class="text-center">
                    <v-chip 
                      color="primary" 
                      size="x-large"
                      variant="elevated"
                      class="mb-3"
                    >
                      {{ profileData.investment_profile.risk_type }}
                    </v-chip>
                    <p class="text-body-2">
                      평가 점수: {{ profileData.investment_profile.total_score }}점
                    </p>
                    <p class="text-caption text-grey">
                      {{ new Date(profileData.investment_profile.evaluated_at).toLocaleDateString() }} 평가
                    </p>
                  </div>
                </v-card>
              </v-col>

              <v-col cols="12" md="4">
                <v-card variant="outlined" class="pa-4 h-100">
                  <h4 class="text-h6 mb-3">투자 목표</h4>
                  <v-list density="compact">
                    <v-list-item>
                      <v-list-item-title>목표 수익률</v-list-item-title>
                      <v-list-item-subtitle>연 {{ profileData.investment_goal.expected_annual_return }}%</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>선호 투자기간</v-list-item-title>
                      <v-list-item-subtitle>{{ profileData.investment_goal.preferred_period }}개월</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>달성 상태</v-list-item-title>
                      <v-list-item-subtitle>
                        <v-chip 
                          size="small" 
                          :color="getStatusColor(profileData.investment_goal.achievement_status)"
                        >
                          {{ profileData.investment_goal.achievement_status }}
                        </v-chip>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 현재 자산 업데이트 다이얼로그 -->
    <v-dialog v-model="showUpdateAssetDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h5 pa-4">
          현재 자산 업데이트
        </v-card-title>
        
        <v-card-text>
          <v-text-field
            v-model.number="newAssetAmount"
            label="현재 자산 (만원)"
            type="number"
            variant="outlined"
            prefix="₩"
            suffix="만원"
            :rules="assetRules"
          />
          <v-alert type="info" variant="tonal" density="compact">
            정확한 투자 목표 달성도 추적을 위해 주기적으로 현재 자산을 업데이트하세요.
          </v-alert>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showUpdateAssetDialog = false">취소</v-btn>
          <v-btn 
            color="primary" 
            variant="elevated"
            @click="updateCurrentAsset"
            :loading="updatingAsset"
          >
            업데이트
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/NavigationBar.vue'
import { useAuthStore } from '@/stores/auth'
import { investmentAPI } from '@/services/api'

const router = useRouter()
const auth = useAuthStore()

// 상태 관리
const loading = ref(false)
const error = ref('')
const profileStatus = ref({ investment_profile: false, investment_goal: false })
const profileData = ref(null)
const goalProgress = ref(null)
const showUpdateAssetDialog = ref(false)
const newAssetAmount = ref(0)
const updatingAsset = ref(false)

// Computed
const completionRate = computed(() => {
  const total = 2
  const completed = (profileStatus.value.investment_profile ? 1 : 0) + 
                   (profileStatus.value.investment_goal ? 1 : 0)
  return (completed / total) * 100
})

// Validation rules
const assetRules = [
  v => !!v || '현재 자산을 입력하세요',
  v => v > 0 || '현재 자산은 0보다 커야 합니다',
  v => v <= 1000000 || '현재 자산은 10억원(100만 만원) 이하여야 합니다'
]

// Methods
async function fetchStatus() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await investmentAPI.checkStatus()
    profileStatus.value = {
      investment_profile: data.has_investment_profile,
      investment_goal: data.has_investment_goal
    }
    
    // 프로필 데이터 가져오기
    if (data.has_investment_profile || data.has_investment_goal) {
      const res = await investmentAPI.getProfile()
      profileData.value = res.data
    }
    
    // 투자 목표 진행 상황 가져오기
    if (data.has_investment_goal) {
      await fetchGoalProgress()
    }
  } catch (e) {
    error.value = e.response?.data?.detail || '프로필 상태 조회 중 오류가 발생했습니다.'
    if (e.response?.status === 401) {
      auth.clearAuth()
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

async function fetchGoalProgress() {
  try {
    const { data } = await investmentAPI.getGoalProgress()
    goalProgress.value = data
    newAssetAmount.value = data.current_asset
  } catch (e) {
    console.error('목표 진행 상황 조회 실패:', e)
  }
}

async function updateCurrentAsset() {
  updatingAsset.value = true
  try {
    await investmentAPI.updateCurrentAsset({
      current_asset: newAssetAmount.value
    })
    showUpdateAssetDialog.value = false
    await fetchStatus() // 전체 데이터 새로고침
    
    // 성공 메시지 (Vuetify snackbar 사용 가능)
    if (goalProgress.value?.progress_percentage >= 100) {
      alert('축하합니다! 투자 목표를 달성했습니다! 🎉')
    }
  } catch (e) {
    error.value = e.response?.data?.error || '자산 업데이트 중 오류가 발생했습니다.'
  } finally {
    updatingAsset.value = false
  }
}

// Utility functions
function formatCurrency(value) {
  return new Intl.NumberFormat('ko-KR').format(value)
}

function getProgressColor(percentage) {
  if (percentage >= 80) return 'success'
  if (percentage >= 50) return 'primary'
  if (percentage >= 25) return 'warning'
  return 'error'
}

function getStatusColor(status) {
  const statusColors = {
    '달성완료': 'success',
    '달성임박': 'primary',
    '순조로운진행': 'info',
    '초기단계': 'warning',
    '시작단계': 'grey'
  }
  return statusColors[status] || 'grey'
}

// Navigation
function goToSurvey() {
  router.push({ name: 'survey' })
}

function goToGoalSetting() {
  router.push('/investment-goal')
}

function goToRecommendations() {
  if (!profileStatus.value.investment_profile || !profileStatus.value.investment_goal) {
    alert('투자 성향 분석과 투자 목표 설정을 모두 완료해주세요.');
    return;
  }
  router.push('/recommendations');
}

// Lifecycle
onMounted(() => {
  if (!auth.token) {
    router.push('/login')
  } else {
    fetchStatus()
  }
})
</script>

<style scoped>
/* 카드 스타일 */
.rounded-lg {
  border-radius: 12px !important;
}

/* 버튼 스타일 */
.v-btn {
  text-transform: none;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 프로그레스 서클 */
.v-progress-circular {
  transition: all 0.3s ease;
}

/* 리스트 아이템 호버 효과 */
.v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

/* 카드 타이틀 배경 */
.bg-primary {
  background-color: #1976D2 !important;
}

.bg-indigo {
  background-color: #3F51B5 !important;
}

.bg-teal {
  background-color: #009688 !important;
}

/* 컨테이너 최대 너비 */
.v-container {
  max-width: 1440px;
  margin: 0 auto;
}

/* 네비게이션 바 아래 여백 */
.mt-8 {
  margin-top: 5rem !important;
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .text-h3 {
    font-size: 2rem !important;
  }
  
  .text-h5 {
    font-size: 1.25rem !important;
  }

  .v-container {
    padding: 16px !important;
  }

  .mt-8 {
    margin-top: 4rem !important;
  }

  .pa-6 {
    padding: 16px !important;
  }

  .v-progress-circular {
    width: 120px !important;
    height: 120px !important;
  }

  .text-h4 {
    font-size: 1.5rem !important;
  }
}

/* 모바일 환경 */
@media (max-width: 600px) {
  .text-h3 {
    font-size: 1.75rem !important;
  }

  .v-progress-circular {
    width: 100px !important;
    height: 100px !important;
  }

  .text-h4 {
    font-size: 1.25rem !important;
  }

  .v-chip {
    font-size: 0.875rem !important;
  }
}

/* 애니메이션 */
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 25px 0 rgba(0, 0, 0, 0.1);
}

/* 칩 스타일 */
.v-chip {
  font-weight: 500;
}

/* 높이 일정하게 유지 */
.h-100 {
  height: 100%;
}

/* 다이얼로그 스타일 */
.v-dialog .v-card {
  border-radius: 12px;
  overflow: hidden;
}

/* 프로그레스 바 스타일 */
.v-progress-linear {
  border-radius: 4px;
  overflow: hidden;
}

/* 아이콘 스타일 */
.v-icon {
  transition: all 0.3s ease;
}

.v-icon:hover {
  transform: scale(1.1);
}

/* 리스트 스타일 */
.v-list {
  background: transparent !important;
}

.v-list-item {
  border-radius: 8px;
  margin-bottom: 4px;
}
</style>