<template>
  <v-container fluid class="mt-8">
    <NavigationBar />
    
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <!-- 헤더 -->
        <div class="text-center mb-6">
          <h1 class="text-h3 font-weight-bold mb-2">투자 목표 설정</h1>
          <p class="text-subtitle-1 text-grey-darken-1">
            {{ hasExistingGoal ? '투자 목표를 수정하세요' : '달성하고 싶은 투자 목표를 설정하세요' }}
          </p>
        </div>

        <!-- 목표 설정 카드 -->
        <v-card elevation="3" class="rounded-lg">
          <v-card-title class="text-h5 py-4 px-6 bg-primary text-white">
            <v-icon class="mr-3">mdi-target</v-icon>
            {{ hasExistingGoal ? '투자 목표 수정' : '새로운 투자 목표' }}
          </v-card-title>

          <v-form ref="form" v-model="valid" @submit.prevent="submitGoal">
            <v-card-text class="pa-6">
              <!-- 현재 자산 -->
              <v-text-field
                v-model.number="goalData.current_asset"
                label="현재 자산"
                type="number"
                variant="outlined"
                prefix="₩"
                suffix="만원"
                :rules="currentAssetRules"
                required
                class="mb-4"
                min="1"
                max="1000000"
                @input="validateNumber($event, 'current_asset')"
              >
                <template v-slot:append-inner>
                  <v-tooltip text="현재 보유하고 있는 총 자산을 입력하세요">
                    <template v-slot:activator="{ props }">
                      <v-icon v-bind="props" size="small">mdi-help-circle-outline</v-icon>
                    </template>
                  </v-tooltip>
                </template>
              </v-text-field>

              <!-- 목표 자산 -->
              <v-text-field
                v-model.number="goalData.target_asset"
                label="목표 자산"
                type="number"
                variant="outlined"
                prefix="₩"
                suffix="만원"
                :rules="targetAssetRules"
                required
                class="mb-4"
                min="1"
                max="10000000"
                @input="validateNumber($event, 'target_asset')"
              >
                <template v-slot:append-inner>
                  <v-tooltip text="달성하고 싶은 목표 자산을 입력하세요">
                    <template v-slot:activator="{ props }">
                      <v-icon v-bind="props" size="small">mdi-help-circle-outline</v-icon>
                    </template>
                  </v-tooltip>
                </template>
              </v-text-field>

              <!-- 목표 기간 -->
              <v-text-field
                v-model.number="goalData.target_years"
                label="목표 달성 기간"
                type="number"
                variant="outlined"
                suffix="년"
                :rules="targetYearsRules"
                required
                class="mb-4"
                min="1"
                max="50"
                @input="validateNumber($event, 'target_years')"
              >
                <template v-slot:append-inner>
                  <v-tooltip text="목표를 달성하고자 하는 기간을 입력하세요">
                    <template v-slot:activator="{ props }">
                      <v-icon v-bind="props" size="small">mdi-help-circle-outline</v-icon>
                    </template>
                  </v-tooltip>
                </template>
              </v-text-field>

              <!-- 선호 투자 기간 -->
              <v-select
                v-model="goalData.preferred_period"
                :items="periodOptions"
                label="선호 투자 기간"
                variant="outlined"
                required
                class="mb-4"
              >
                <template v-slot:append-inner>
                  <v-tooltip text="단기/중기/장기 중 선호하는 투자 기간을 선택하세요">
                    <template v-slot:activator="{ props }">
                      <v-icon v-bind="props" size="small">mdi-help-circle-outline</v-icon>
                    </template>
                  </v-tooltip>
                </template>
              </v-select>

              <!-- 필요 수익률 계산 결과 -->
              <v-alert 
                v-if="calculatedReturn !== null"
                :type="getReturnAlertType()"
                variant="tonal"
                class="mb-4"
              >
                <v-alert-title>필요 연평균 수익률</v-alert-title>
                <div class="text-h5 font-weight-bold mt-2">{{ calculatedReturn }}%</div>
                <div class="mt-2">{{ getReturnMessage() }}</div>
              </v-alert>

              <!-- 투자 계획 시뮬레이션 -->
              <v-expansion-panels v-if="calculatedReturn !== null" class="mb-4">
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon class="mr-2">mdi-calculator</v-icon>
                    투자 계획 시뮬레이션
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-simple-table density="comfortable">
                      <template v-slot:default>
                        <tbody>
                          <tr>
                            <td>월 필요 저축액</td>
                            <td class="text-right font-weight-bold">
                              {{ formatCurrency(getMonthlyRequired()) }}만원
                            </td>
                          </tr>
                          <tr>
                            <td>예상 최종 자산</td>
                            <td class="text-right font-weight-bold">
                              {{ formatCurrency(goalData.target_asset) }}만원
                            </td>
                          </tr>
                          <tr>
                            <td>총 수익금</td>
                            <td class="text-right font-weight-bold">
                              {{ formatCurrency(goalData.target_asset - goalData.current_asset) }}만원
                            </td>
                          </tr>
                        </tbody>
                      </template>
                    </v-simple-table>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card-text>

            <!-- 액션 버튼 -->
            <v-card-actions class="justify-center pa-6 bg-grey-lighten-5">
              <v-btn
                variant="text"
                size="large"
                @click="router.push('/investment-profile')"
              >
                취소
              </v-btn>
              <v-btn
                type="submit"
                color="primary"
                variant="elevated"
                size="large"
                :loading="submitting"
                :disabled="!valid"
              >
                {{ hasExistingGoal ? '목표 수정' : '목표 설정' }}
              </v-btn>
            </v-card-actions>
          </v-form>
        </v-card>

        <!-- 목표 설정 도움말 -->
        <v-card variant="outlined" class="mt-6">
          <v-card-text>
            <h3 class="text-h6 mb-3">
              <v-icon class="mr-2">mdi-lightbulb-outline</v-icon>
              목표 설정 가이드
            </h3>
            <v-list density="compact">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon size="small" color="primary">mdi-check</v-icon>
                </template>
                <v-list-item-title>현실적인 목표를 설정하세요</v-list-item-title>
                <v-list-item-subtitle>연 10-15% 이상의 수익률은 높은 위험을 동반합니다</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon size="small" color="primary">mdi-check</v-icon>
                </template>
                <v-list-item-title>장기 투자를 고려하세요</v-list-item-title>
                <v-list-item-subtitle>시간이 길수록 복리 효과를 극대화할 수 있습니다</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon size="small" color="primary">mdi-check</v-icon>
                </template>
                <v-list-item-title>정기적으로 목표를 검토하세요</v-list-item-title>
                <v-list-item-subtitle>상황 변화에 따라 목표를 조정하는 것이 중요합니다</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/NavigationBar.vue'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/services/api'

const router = useRouter()
const auth = useAuthStore()

// 상태 관리
const form = ref(null)
const valid = ref(false)
const submitting = ref(false)
const hasExistingGoal = ref(false)
const calculatedReturn = ref(null)

// 폼 데이터
const goalData = ref({
  current_asset: '',
  target_asset: '',
  target_years: '',
  preferred_period: 12
})

// 선택 옵션
const periodOptions = [
  { title: '3개월 (단기)', value: 3 },
  { title: '6개월 (단기)', value: 6 },
  { title: '12개월 (중기)', value: 12 },
  { title: '24개월 (중기)', value: 24 },
  { title: '36개월 (장기)', value: 36 },
  { title: '60개월 (장기)', value: 60 }
]

// 유효성 검사 규칙
const currentAssetRules = [
  v => !!v || '현재 자산을 입력하세요',
  v => v > 0 || '현재 자산은 0보다 커야 합니다',
  v => v <= 1000000 || '현재 자산은 10억원 이하여야 합니다'
]

const targetAssetRules = [
  v => !!v || '목표 자산을 입력하세요',
  v => v > 0 || '목표 자산은 0보다 커야 합니다',
  v => v <= 10000000 || '목표 자산은 100억원 이하여야 합니다',
  v => !goalData.value.current_asset || v > goalData.value.current_asset || '목표 자산은 현재 자산보다 커야 합니다'
]

const targetYearsRules = [
  v => !!v || '목표 기간을 입력하세요',
  v => v >= 1 || '목표 기간은 1년 이상이어야 합니다',
  v => v <= 50 || '목표 기간은 50년 이하여야 합니다'
]

// Watch: 필요 수익률 자동 계산
watch([
  () => goalData.value.current_asset,
  () => goalData.value.target_asset,
  () => goalData.value.target_years
], () => {
  // 숫자 형식으로 변환
  goalData.value.current_asset = goalData.value.current_asset ? parseInt(goalData.value.current_asset) || '' : ''
  goalData.value.target_asset = goalData.value.target_asset ? parseInt(goalData.value.target_asset) || '' : ''
  goalData.value.target_years = goalData.value.target_years ? parseInt(goalData.value.target_years) || '' : ''

  // 필요 수익률 계산
  if (goalData.value.current_asset && goalData.value.target_asset && goalData.value.target_years) {
    const r = Math.pow(goalData.value.target_asset / goalData.value.current_asset, 1 / goalData.value.target_years) - 1
    calculatedReturn.value = Math.round(r * 100 * 100) / 100
  } else {
    calculatedReturn.value = null
  }
})

// Methods
async function fetchExistingGoal() {
  try {
    const { data } = await apiClient.getGoal()
    hasExistingGoal.value = true
    goalData.value = {
      current_asset: data.current_asset,
      target_asset: data.target_asset,
      target_years: data.target_years,
      preferred_period: data.preferred_period
    }
  } catch (e) {
    if (e.response?.status === 404) {
      hasExistingGoal.value = false
    } else {
      console.error('목표 조회 실패:', e)
    }
  }
}

async function submitGoal() {
  if (!form.value.validate()) return

  submitting.value = true
  try {
    // 데이터 형식 변환 및 검증
    const formattedData = {
      current_asset: parseInt(goalData.value.current_asset),
      target_asset: parseInt(goalData.value.target_asset),
      target_years: parseInt(goalData.value.target_years),
      preferred_period: parseInt(goalData.value.preferred_period)
    }

    // 데이터 로깅 추가
    console.log('제출할 데이터:', formattedData)

    // 데이터 유효성 검사
    if (isNaN(formattedData.current_asset) || 
        isNaN(formattedData.target_asset) || 
        isNaN(formattedData.target_years) || 
        isNaN(formattedData.preferred_period)) {
      throw new Error('모든 필드를 올바른 숫자로 입력해주세요.')
    }

    // 추가 유효성 검사
    if (formattedData.target_asset <= formattedData.current_asset) {
      throw new Error('목표 자산은 현재 자산보다 커야 합니다.')
    }

    if (formattedData.target_years < 1 || formattedData.target_years > 50) {
      throw new Error('목표 기간은 1년에서 50년 사이여야 합니다.')
    }

    try {
      if (hasExistingGoal.value) {
        // 수정
        const response = await apiClient.updateGoal(formattedData)
        console.log('수정 응답:', response)
      } else {
        // 생성
        const response = await apiClient.createGoal(formattedData)
        console.log('생성 응답:', response)
      }
      
      router.push('/recommendations')
    } catch (apiError) {
      console.error('API 에러:', apiError.response?.data || apiError)
      throw apiError
    }
  } catch (e) {
    // 에러 메시지 개선
    if (e.message) {
      // 클라이언트 측 유효성 검사 에러
      alert(e.message)
    } else if (e.response?.data?.error) {
      // 서버 측 에러 메시지
      alert(e.response.data.error)
      if (e.response.data.details) {
        console.error('상세 에러:', e.response.data.details)
      }
    } else {
      // 기타 에러
      alert('목표 설정 중 오류가 발생했습니다. 입력값을 확인해주세요.')
    }
  } finally {
    submitting.value = false
  }
}

// Utility functions
function formatCurrency(value) {
  return new Intl.NumberFormat('ko-KR').format(value)
}

function getMonthlyRequired() {
  if (!goalData.value.current_asset || !goalData.value.target_asset || !goalData.value.target_years) {
    return 0
  }
  const totalMonths = goalData.value.target_years * 12
  const totalRequired = goalData.value.target_asset - goalData.value.current_asset
  return Math.round(totalRequired / totalMonths * 10) / 10
}

function getReturnAlertType() {
  if (calculatedReturn.value > 30) return 'error'
  if (calculatedReturn.value > 15) return 'warning'
  return 'success'
}

function getReturnMessage() {
  if (calculatedReturn.value > 30) {
    return '매우 높은 수익률입니다. 현실적인 목표 재설정을 권장합니다.'
  }
  if (calculatedReturn.value > 15) {
    return '높은 수익률입니다. 위험 자산 비중이 높은 포트폴리오가 필요합니다.'
  }
  if (calculatedReturn.value > 7) {
    return '적절한 수익률입니다. 균형잡힌 포트폴리오를 구성하세요.'
  }
  return '안정적인 수익률입니다. 예적금과 채권 위주의 투자가 적합합니다.'
}

// 숫자 입력 검증 함수
function validateNumber(event, field) {
  const value = event.target.value
  if (value === '') {
    goalData.value[field] = ''
    return
  }
  
  const num = parseInt(value)
  if (isNaN(num)) {
    goalData.value[field] = ''
    return
  }

  // 범위 검증
  switch (field) {
    case 'current_asset':
      if (num < 1 || num > 1000000) {
        goalData.value[field] = ''
        return
      }
      break
    case 'target_asset':
      if (num < 1 || num > 10000000) {
        goalData.value[field] = ''
        return
      }
      break
    case 'target_years':
      if (num < 1 || num > 50) {
        goalData.value[field] = ''
        return
      }
      break
  }

  goalData.value[field] = num
}

// Lifecycle
onMounted(() => {
  if (!auth.token) {
    router.push('/login')
  } else {
    fetchExistingGoal()
  }
})
</script>

<style scoped>
.rounded-lg {
  border-radius: 12px !important;
}

.v-btn {
  text-transform: none;
  font-weight: 500;
}

.bg-primary {
  background-color: #1976D2 !important;
}

/* 테이블 스타일 */
.v-simple-table td {
  padding: 12px 16px !important;
}

/* 반응형 */
@media (max-width: 600px) {
  .text-h3 {
    font-size: 1.75rem !important;
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

/* 입력 필드 스타일 */
.v-text-field {
  margin-bottom: 1rem;
}

/* 도움말 아이콘 스타일 */
.v-icon.mdi-help-circle-outline {
  opacity: 0.7;
  cursor: help;
}

/* 알림 스타일 */
.v-alert {
  margin-bottom: 1.5rem;
}

/* 확장 패널 스타일 */
.v-expansion-panel {
  margin-bottom: 1rem !important;
}

/* 카드 애니메이션 */
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 25px 0 rgba(0, 0, 0, 0.1);
}
</style> 