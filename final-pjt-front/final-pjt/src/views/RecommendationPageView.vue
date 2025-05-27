<template>
    <v-container fluid class="mt-8">
        <NavigationBar />

        <v-row justify="center">
            <v-col cols="12" lg="10" xl="8">
                <!-- 헤더 섹션 -->
                <div class="text-center mb-6">
                    <h1 class="text-h3 font-weight-bold mb-2">맞춤 투자 상품 추천</h1>
                    <p class="text-subtitle-1 text-grey-darken-1">
                        당신의 투자 성향과 목표에 맞는 상품을 추천해드립니다
                    </p>
                </div>

                <!-- 로딩 상태 -->
                <v-card v-if="loading" elevation="3" class="rounded-lg">
                    <v-card-text class="text-center py-8">
                        <v-progress-circular indeterminate color="primary" size="64" />
                        <p class="mt-4 text-subtitle-1">추천 상품을 불러오는 중...</p>
                    </v-card-text>
                </v-card>

                <!-- 에러 상태 -->
                <v-card v-else-if="error" elevation="3" class="rounded-lg">
                    <v-card-text class="pa-6">
                        <v-alert type="error" variant="tonal">
                            <v-alert-title>오류 발생</v-alert-title>
                            {{ error }}
                        </v-alert>
                        <div class="text-center mt-4">
                            <v-btn color="primary" @click="refreshRecommendations">
                                다시 시도
                            </v-btn>
                        </div>
                    </v-card-text>
                </v-card>

                <!-- 추천 결과 -->
                <template v-else>
                    <!-- 추천 요약 -->
                    <v-card elevation="3" class="mb-6 rounded-lg">
                        <v-card-title class="text-h5 py-4 px-6 bg-primary text-white">
                            <v-icon class="mr-3">mdi-chart-line</v-icon>
                            투자 프로필 요약
                        </v-card-title>
                        <v-card-text class="pa-6">
                            <v-row>
                                <v-col cols="12" md="4">
                                    <div class="text-center">
                                        <h3 class="text-h6 mb-2">투자 성향</h3>
                                        <v-chip
                                            color="primary"
                                            size="large"
                                            class="mb-2"
                                        >
                                            {{ recommendationSummary.risk_type }}
                                        </v-chip>
                                    </div>
                                </v-col>
                                <v-col cols="12" md="4">
                                    <div class="text-center">
                                        <h3 class="text-h6 mb-2">필요 수익률</h3>
                                        <v-chip
                                            color="success"
                                            size="large"
                                            class="mb-2"
                                        >
                                            연 {{ recommendationSummary.required_return }}%
                                        </v-chip>
                                    </div>
                                </v-col>
                                <v-col cols="12" md="4">
                                    <div class="text-center">
                                        <h3 class="text-h6 mb-2">선호 투자기간</h3>
                                        <v-chip
                                            color="info"
                                            size="large"
                                            class="mb-2"
                                        >
                                            {{ recommendationSummary.preferred_period }}개월
                                        </v-chip>
                                    </div>
                                </v-col>
                            </v-row>
                        </v-card-text>
                    </v-card>

                    <!-- 경고 메시지 -->
                    <v-card v-if="error" elevation="3" class="mb-6 rounded-lg">
                        <v-card-text class="pa-6">
                            <v-alert
                                type="warning"
                                variant="tonal"
                                class="mb-0 warning-alert"
                            >
                                <div class="d-flex flex-column">
                                    <div class="d-flex align-center mb-4">
                                        <v-icon icon="mdi-alert" class="mr-2" size="large" />
                                        <span class="text-h6">투자 목표 재검토 필요</span>
                                    </div>
                                    <p class="text-body-1 mb-4">{{ error }}</p>
                                    <div class="d-flex justify-end gap-2">
                                        <v-btn
                                            color="primary"
                                            variant="text"
                                            @click="refreshRecommendations"
                                            class="action-button"
                                        >
                                            <v-icon icon="mdi-refresh" class="mr-2" />
                                            다시 시도
                                        </v-btn>
                                        <v-btn
                                            color="primary"
                                            variant="elevated"
                                            @click="router.push('/investment-profile')"
                                            class="action-button"
                                        >
                                            <v-icon icon="mdi-pencil" class="mr-2" />
                                            투자 프로필 수정하기
                                        </v-btn>
                                    </div>
                                </div>
                            </v-alert>
                        </v-card-text>
                    </v-card>

                    <!-- 추천 상품 목록 -->
                    <v-card v-if="!error && store.items.length > 0" elevation="3" class="rounded-lg">
                        <v-card-title class="text-h5 py-4 px-6 bg-primary text-white">
                            <v-icon class="mr-3">mdi-star</v-icon>
                            추천 상품 목록
                        </v-card-title>
                        <v-card-text class="pa-6">
                            <v-list>
                                <template v-for="item in store.items" :key="item.id">
                                    <RecommendationItem
                                        :item="item"
                                        @save="saveStockRecommendation"
                                    />
                                    <v-divider />
                                </template>
                            </v-list>
                        </v-card-text>
                    </v-card>
                </template>
            </v-col>
        </v-row>

        <!-- 스낵바 -->
        <v-snackbar
            v-model="snackbar"
            :color="snackbarColor"
            timeout="3000"
            location="top"
        >
            {{ snackbarMessage }}
        </v-snackbar>
    </v-container>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useRecommendationStore } from '@/stores/recommendationStore';
import NavigationBar from '@/components/NavigationBar.vue';
import RecommendationItem from '@/components/RecommendationItem.vue';
import { recommendationAPI, investmentAPI } from '@/services/api';

const router = useRouter();
const auth = useAuthStore();
const store = useRecommendationStore();

// store에서 items를 computed로 가져오기
const recommendations = computed(() => store.items || []);
const loading = ref(false);
const error = ref('');

// 상태 관리
const snackbar = ref(false);
const snackbarMessage = ref('');
const snackbarColor = ref('success');

// API 호출 취소를 위한 AbortController
let abortController = null;

// 추천 요약 정보를 store에서 가져오기
const recommendationSummary = computed(() => store.recommendationSummary);

// 추천 상품 저장
async function saveStockRecommendation(stock) {
    if (!stock) {
        showSnackbar('저장할 상품이 없습니다.', 'error');
        return;
    }

    try {
        await recommendationAPI.saveStocks(stock);
        showSnackbar('추천 상품이 저장되었습니다.', 'success');
    } catch (err) {
        console.error('추천 저장 실패:', err);
        showSnackbar(err.message || '추천 상품 저장에 실패했습니다.', 'error');
    }
}

// 스낵바 표시
function showSnackbar(message, color = 'success') {
    snackbarMessage.value = message;
    snackbarColor.value = color;
    snackbar.value = true;
}

// 추천 상품 새로고침
async function refreshRecommendations() {
    if (abortController) {
        abortController.abort();
    }
    abortController = new AbortController();

    loading.value = true;
    error.value = '';
    try {
        // 1. 투자 프로필 정보 가져오기
        const profileResponse = await investmentAPI.getProfile();
        if (!profileResponse?.data) {
            throw new Error('투자 프로필 정보를 불러올 수 없습니다.');
        }

        // 2. 추천 상품 가져오기
        const response = await recommendationAPI.getByGoal();
        if (!response?.data) {
            throw new Error('추천 데이터를 불러올 수 없습니다.');
        }

        // 경고 메시지가 있는 경우 처리
        if (response.data.warning) {
            error.value = response.data.message || '현재 투자 성향으로는 목표 수익률 달성이 어렵습니다.';
            store.items = [];
            store.recommendationSummary = {
                risk_type: response.data.factors?.by_risk || '',
                required_return: response.data.required_return || 0,
                preferred_period: response.data.factors?.preferred_period || 0
            };
            return;
        }

        // 정상적인 추천 상품 목록 업데이트
        store.items = response.data.items || [];
        
        // store의 recommendationSummary 업데이트
        store.recommendationSummary = {
            risk_type: response.data.factors?.by_risk || '',
            required_return: response.data.required_return || 0,
            preferred_period: response.data.factors?.preferred_period || 0
        };
        
    } catch (err) {
        if (err.name === 'AbortError') {
            console.log('API 요청이 취소되었습니다.');
            return;
        }
        console.error('데이터 조회 실패:', err);
        error.value = err.message || '데이터를 불러오는데 실패했습니다.';
        showSnackbar(error.value, 'error');
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

onMounted(async () => {
    if (!auth.token) {
        router.push('/login');
        return;
    }
    // store.items 초기화
    store.items = [];
    await refreshRecommendations();
});

// 컴포넌트 언마운트 전 정리
onBeforeUnmount(() => {
    if (abortController) {
        abortController.abort();
    }
    // 상태 초기화
    loading.value = false;
    error.value = '';
    showSnackbar();
    // store 정리
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

.warning-alert {
    border-radius: 12px;
}

.action-button {
    min-width: 160px;
}

.gap-2 {
    gap: 8px;
}
</style>