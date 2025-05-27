<template>
    <v-container fluid class="mt-8">
        <NavigationBar />
        
        <v-row justify="center">
            <v-col cols="12" lg="10" xl="8">
                <!-- 헤더 섹션 -->
                <div class="text-center mb-6">
                    <h1 class="text-h3 font-weight-bold mb-2">맞춤 투자 추천</h1>
                    <p class="text-subtitle-1 text-grey-darken-1">
                        투자 성향과 목표에 맞는 최적의 상품을 추천해드립니다
                    </p>
                </div>

                <!-- 추천 요약 카드 -->
                <v-card elevation="3" class="mb-6 rounded-lg">
                    <v-card-title class="text-h5 py-4 px-6 bg-primary text-white">
                        <v-icon class="mr-3">mdi-lightbulb</v-icon>
                        추천 전략
                    </v-card-title>
                    <v-card-text class="pa-6">
                        <v-row>
                            <v-col cols="12" md="4">
                                <v-card variant="outlined" class="pa-4 h-100">
                                    <h4 class="text-h6 mb-3">
                                        <v-icon color="primary" class="mr-2">mdi-account</v-icon>
                                        투자 성향
                                    </h4>
                                    <v-chip color="primary" variant="elevated" class="mb-2">
                                        {{ recommendationSummary.risk_type || '불러오는 중...' }}
                                    </v-chip>
                                </v-card>
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-card variant="outlined" class="pa-4 h-100">
                                    <h4 class="text-h6 mb-3">
                                        <v-icon color="success" class="mr-2">mdi-trending-up</v-icon>
                                        목표 수익률
                                    </h4>
                                    <v-chip color="success" variant="elevated" class="mb-2">
                                        연 {{ recommendationSummary.required_return || 0 }}%
                                    </v-chip>
                                </v-card>
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-card variant="outlined" class="pa-4 h-100">
                                    <h4 class="text-h6 mb-3">
                                        <v-icon color="info" class="mr-2">mdi-clock-outline</v-icon>
                                        선호 기간
                                    </h4>
                                    <v-chip color="info" variant="elevated" class="mb-2">
                                        {{ recommendationSummary.preferred_period || 0 }}개월
                                    </v-chip>
                                </v-card>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <!-- 필터 섹션 -->
                <v-card v-if="recommendationSummary.risk_type.includes('주식')" elevation="3" class="mb-6 rounded-lg">
                    <v-card-title class="text-h5 py-4 px-6 bg-primary text-white">
                        <v-icon class="mr-3">mdi-filter-variant</v-icon>
                        추천 필터
                    </v-card-title>
                    <v-card-text class="pa-6">
                        <v-row>
                            <v-col cols="12" sm="6">
                                <v-select
                                    v-model="selectedMarket"
                                    :items="marketOptions"
                                    label="시장 선택"
                                    variant="outlined"
                                    clearable
                                    @update:model-value="refreshRecommendations"
                                />
                            </v-col>
                            <v-col cols="12" sm="6">
                                <v-select
                                    v-model="selectedSector"
                                    :items="sectorOptions"
                                    label="섹터 선택"
                                    variant="outlined"
                                    clearable
                                    @update:model-value="refreshRecommendations"
                                />
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <!-- 추천 결과 -->
                <v-card elevation="3" class="rounded-lg">
                    <v-card-title class="text-h5 py-4 px-6 bg-primary text-white">
                        <v-icon class="mr-3">mdi-star</v-icon>
                        추천 상품
                    </v-card-title>

                    <!-- 로딩 상태 -->
                    <v-card-text v-if="loading" class="text-center py-8">
                        <v-progress-circular indeterminate color="primary" size="64" />
                        <p class="mt-4 text-subtitle-1">추천 상품을 불러오는 중...</p>
                    </v-card-text>

                    <!-- 에러 상태 -->
                    <v-card-text v-else-if="error" class="pa-6">
                        <v-alert type="error" variant="tonal">
                            <v-alert-title>오류 발생</v-alert-title>
                            {{ error }}
                            <template v-slot:append>
                                <v-btn color="error" variant="text" @click="refreshRecommendations">
                                    다시 시도
                                </v-btn>
                            </template>
                        </v-alert>
                    </v-card-text>

                    <!-- 추천 결과 -->
                    <v-card-text v-else class="pa-6">
                        <RecommendationList 
                            :items="recommendations" 
                            :loading="loading" 
                            :error="error"
                            @save-stock="saveStockRecommendation"
                        />
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <!-- 성공 스낵바 -->
        <v-snackbar
            v-model="showSuccessSnackbar"
            color="success"
            timeout="3000"
        >
            {{ snackbarMessage }}
            <template v-slot:actions>
                <v-btn
                    color="white"
                    variant="text"
                    @click="showSuccessSnackbar = false"
                >
                    닫기
                </v-btn>
            </template>
        </v-snackbar>
    </v-container>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useRecommendationStore } from '@/stores/recommendationStore';
import RecommendationList from '@/components/RecommendationList.vue';
import NavigationBar from '@/components/NavigationBar.vue';
import { recommendationAPI } from '@/services/api';

const router = useRouter();
const auth = useAuthStore();
const store = useRecommendationStore();

// 컴포넌트 참조
const recommendationListRef = ref(null);

// store에서 items를 computed로 가져오기
const recommendations = computed(() => store.items || []);
const loading = ref(false);
const error = ref(null);

// 상태 관리
const selectedMarket = ref(null);
const selectedSector = ref(null);
const showSuccessSnackbar = ref(false);
const snackbarMessage = ref('');
const recommendationSummary = ref({
    risk_type: '',
    required_return: 0,
    preferred_period: 0
});

// 필터 옵션
const marketOptions = ['KOSPI', 'KOSDAQ', 'KONEX'];
const sectorOptions = [
    '반도체', '바이오', '2차전지', '자동차',
    '금융', '건설', '에너지', '유통', '플랫폼', '기타'
];

// 추천 데이터 새로고침
async function refreshRecommendations() {
    if (!auth.token) return;
    
    loading.value = true;
    error.value = null;
    
    try {
        const response = await recommendationAPI.getByGoal({
            market: selectedMarket.value,
            sector: selectedSector.value
        });
        
        if (!response?.data) {
            throw new Error('응답 데이터가 올바르지 않습니다.');
        }

        console.log('API 응답:', response.data);

        // 추천 요약 정보 업데이트
        recommendationSummary.value = {
            risk_type: response.data.factors?.by_risk || '',
            required_return: response.data.required_return || 0,
            preferred_period: response.data.factors?.preferred_period || 0
        };

        // 추천 상품 목록 업데이트
        store.items = response.data.items || [];
        
    } catch (err) {
        console.error('추천 데이터 조회 실패:', err);
        error.value = err.message || '추천 데이터를 불러오는데 실패했습니다.';
        if (err.response?.status === 401) {
            auth.clearAuth();
            router.push('/login');
        } else if (err.response?.status === 404) {
            router.push('/investment-profile');
        }
    } finally {
        loading.value = false;
    }
}

// 주식 추천 저장
async function saveStockRecommendation(stock) {
    if (!stock) return;
    
    try {
        await store.saveStockRecommendations([stock]);
        showSuccessSnackbar.value = true;
        snackbarMessage.value = '추천 종목이 저장되었습니다.';
    } catch (err) {
        console.error('추천 저장 실패:', err);
        error.value = err.message || '추천 종목 저장에 실패했습니다.';
    }
}

onMounted(async () => {
    if (!auth.token) {
        router.push('/login');
        return;
    }
    await refreshRecommendations();
});

// 컴포넌트 언마운트 전 정리 작업
onBeforeUnmount(() => {
    // 참조 정리
    if (recommendationListRef.value) {
        recommendationListRef.value = null;
    }
    
    // 상태 초기화
    loading.value = false;
    error.value = null;
    showSuccessSnackbar.value = false;
    snackbarMessage.value = '';
    
    // 스토어 상태 정리
    store.clearState();
});
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
}

/* 모바일 환경 */
@media (max-width: 600px) {
    .text-h3 {
        font-size: 1.75rem !important;
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

/* 높이 일정하게 유지 */
.h-100 {
    height: 100%;
}

/* 칩 스타일 */
.v-chip {
    font-weight: 500;
}
</style>