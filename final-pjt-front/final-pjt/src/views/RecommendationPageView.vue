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
                        <v-row class="mt-4">
                            <v-col cols="12" class="text-center">
                                <v-btn color="primary" size="large" prepend-icon="mdi-magnify"
                                    @click="getRecommendations" :loading="loading" class="recommend-btn">
                                    맞춤 상품 추천받기
                                </v-btn>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <!-- 필터 섹션 -->
                <v-card v-if="isStockInvestmentAvailable" elevation="3" class="mb-6 rounded-lg">
                    <v-card-title class="text-h5 py-4 px-6 bg-primary text-white">
                        <v-icon class="mr-3">mdi-filter-variant</v-icon>
                        추천 필터
                    </v-card-title>
                    <v-card-text class="pa-6">
                        <v-row>
                            <v-col cols="12" sm="6">
                                <v-select v-model="selectedMarket" :items="[
                                    { title: '전체 시장', value: 'ALL' },
                                    ...marketOptions.map(market => ({ title: market, value: market }))
                                ]" label="시장 선택" variant="outlined" item-title="title" item-value="value" />
                            </v-col>
                            <v-col cols="12" sm="6">
                                <v-select v-model="selectedSector" :items="[
                                    { title: '전체 산업군', value: 'ALL' },
                                    ...sectorOptions.map(sector => ({ title: sector, value: sector }))
                                ]" label="섹터 선택" variant="outlined" item-title="title" item-value="value" />
                            </v-col>
                        </v-row>
                        <v-row>
                            <v-col cols="12" class="d-flex justify-end gap-2">
                                <v-btn color="primary" variant="outlined" prepend-icon="mdi-refresh"
                                    @click="clearFilters">
                                    필터 초기화
                                </v-btn>
                                <v-btn color="primary" prepend-icon="mdi-magnify" @click="applyFilters"
                                    :loading="loading">
                                    검색
                                </v-btn>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <!-- 추천 결과 -->
                <v-card v-if="hasRecommendations" elevation="3" class="rounded-lg">
                    <v-card-title
                        class="text-h5 py-4 px-6 bg-primary text-white d-flex justify-space-between align-center">
                        <div>
                            <v-icon class="mr-3">mdi-star</v-icon>
                            추천 상품
                        </div>
                        <v-btn v-if="filteredRecommendations.length > 0" color="white" variant="text"
                            prepend-icon="mdi-content-save" @click="saveAllRecommendations" :loading="saving">
                            전체 저장
                        </v-btn>
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
                        <RecommendationList :items="filteredRecommendations" :loading="loading" :error="error"
                            @save-stock="saveStockRecommendation" />
                    </v-card-text>
                </v-card>

                <!-- 저장된 추천 섹션 -->
                <v-card v-if="savedRecommendations.length > 0" elevation="3" class="mt-6 rounded-lg">
                    <v-card-title
                        class="text-h5 py-4 px-6 bg-success text-white d-flex justify-space-between align-center">
                        <div>
                            <v-icon class="mr-3">mdi-bookmark-check</v-icon>
                            저장된 추천 상품 ({{ savedRecommendations.length }})
                        </div>
                        <v-btn color="white" variant="text" prepend-icon="mdi-delete-sweep"
                            @click="clearAllSavedRecommendations" :loading="clearingAll" :disabled="clearingAll">
                            전체 삭제
                        </v-btn>
                    </v-card-title>
                    <v-card-text class="pa-6">
                        <v-list>
                            <v-list-item v-for="(item, index) in savedRecommendations" :key="index"
                                class="mb-2 saved-item">
                                <template v-slot:prepend>
                                    <v-icon :color="getMarketColor(item.market)" class="mr-2">
                                        {{ getMarketIcon(item.market) }}
                                    </v-icon>
                                </template>
                                <v-list-item-title class="font-weight-bold">{{ item.name }}</v-list-item-title>
                                <v-list-item-subtitle>
                                    <span v-if="item.market">{{ item.market }}</span>
                                    <span v-if="item.sector" class="ml-2">{{ item.sector }}</span>
                                </v-list-item-subtitle>
                                <template v-slot:append>
                                    <v-btn icon color="error" variant="text" size="small"
                                        @click="deleteRecommendation(item.id)" :loading="deletingId === item.id"
                                        :disabled="deletingId === item.id" class="delete-btn">
                                        <v-icon>mdi-delete</v-icon>
                                    </v-btn>
                                </template>
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <!-- 성공 스낵바 -->
        <v-snackbar v-model="showSuccessSnackbar" color="success" timeout="3000">
            {{ snackbarMessage }}
            <template v-slot:actions>
                <v-btn color="white" variant="text" @click="showSuccessSnackbar = false">
                    닫기
                </v-btn>
            </template>
        </v-snackbar>
    </v-container>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useRecommendationStore } from '@/stores/recommendationStore';
import RecommendationList from '@/components/RecommendationList.vue';
import NavigationBar from '@/components/NavigationBar.vue';
import { recommendationAPI } from '@/services/api';

const router = useRouter();
const auth = useAuthStore();
const store = useRecommendationStore();

// 상태 관리
const loading = computed(() => store.isLoading);
const error = computed(() => store.getError);
const selectedMarket = ref(null);
const selectedSector = ref(null);
const showSuccessSnackbar = ref(false);
const snackbarMessage = ref('');
const saving = ref(false);
const deletingId = ref(null);
const clearingAll = ref(false);
const hasRecommendations = ref(false);

// auth 상태 감시
watch(() => auth.token, (newToken) => {
    if (!newToken) {
        // 로그아웃 시 상태 초기화
        store.clearState();
        selectedMarket.value = null;
        selectedSector.value = null;
        hasRecommendations.value = false;
        showSuccessSnackbar.value = false;
        snackbarMessage.value = '';

        // 로그인 페이지로 리다이렉트
        router.push('/login');
    }
});

// 추천 요약 정보
const recommendationSummary = computed(() => store.recommendationSummary);

// 필터링된 추천 상품
const filteredRecommendations = computed(() => store.filteredItems);

// 저장된 추천 상품
const savedRecommendations = computed(() => store.savedRecommendations);

// 필터 옵션
const marketOptions = ['KOSPI', 'KOSDAQ', 'KONEX'];
const sectorOptions = [
    '반도체', '바이오', '2차전지', '자동차',
    '금융', '건설', '에너지', '유통', '플랫폼', '기타'
];

// 주식 투자 가능 여부 계산
const isStockInvestmentAvailable = computed(() => {
    const riskType = recommendationSummary.value?.risk_type;
    const requiredReturn = recommendationSummary.value?.required_return || 0;

    if (riskType === '적극투자형' || riskType === '공격투자형') {
        return requiredReturn > 5.0;
    } else if (riskType === '위험중립형') {
        return requiredReturn > 7.0;
    }
    return false;
});

// 필터 적용
function applyFilters() {
    const filters = {
        market: selectedMarket.value || 'ALL',  // 선택하지 않으면 'ALL'로 설정
        sector: selectedSector.value || 'ALL'   // 선택하지 않으면 'ALL'로 설정
    };
    store.setFilter('market', filters.market);
    store.setFilter('sector', filters.sector);
}

// 필터 초기화
function clearFilters() {
    selectedMarket.value = null;
    selectedSector.value = null;
    store.clearFilters();
}

// 추천 데이터 새로고침
async function refreshRecommendations() {
    try {
        await store.fetchRecommendations();
    } catch (err) {
        console.error('추천 데이터 조회 실패:', err);
        if (err.response?.status === 401) {
            auth.clearAuth();
            router.push('/login');
        } else if (err.response?.status === 404) {
            router.push('/investment-profile');
        }
    }
}

// 추천 받기
async function getRecommendations() {
    try {
        await store.fetchRecommendations();
        hasRecommendations.value = true;
    } catch (err) {
        console.error('추천 데이터 조회 실패:', err);
        if (err.response?.status === 401) {
            auth.clearAuth();
            router.push('/login');
        } else if (err.response?.status === 404) {
            router.push('/investment-profile');
        }
    }
}

// 주식 추천 저장
async function saveStockRecommendation(stock) {
    try {
        await store.saveStockRecommendations([stock]);
        showSuccessSnackbar.value = true;
        snackbarMessage.value = '추천 종목이 저장되었습니다.';
    } catch (err) {
        console.error('추천 저장 실패:', err);
    }
}

// 전체 추천 저장
async function saveAllRecommendations() {
    if (!filteredRecommendations.value.length) return;

    saving.value = true;
    try {
        await store.saveStockRecommendations(filteredRecommendations.value);
        showSuccessSnackbar.value = true;
        snackbarMessage.value = '추천 종목이 저장되었습니다.';
    } catch (err) {
        console.error('추천 저장 실패:', err);
        showSuccessSnackbar.value = true;
        snackbarMessage.value = '추천 종목 저장에 실패했습니다.';
    } finally {
        saving.value = false;
    }
}

// 전체 추천 상품 삭제
async function clearAllSavedRecommendations() {
    if (!confirm('정말로 모든 저장된 추천 상품을 삭제하시겠습니까?')) return;

    clearingAll.value = true;
    try {
        await store.deleteAllSavedRecommendations();
        showSuccessSnackbar.value = true;
        snackbarMessage.value = '모든 추천 상품이 삭제되었습니다.';

        // 저장된 추천 목록 새로고침
        await store.fetchSavedRecommendations();
    } catch (err) {
        console.error('전체 삭제 실패:', err);
        showSuccessSnackbar.value = true;
        snackbarMessage.value = '추천 상품 삭제에 실패했습니다.';
    } finally {
        clearingAll.value = false;
    }
}

// 개별 추천 상품 삭제
async function deleteRecommendation(id) {
    if (!confirm('정말로 이 추천 상품을 삭제하시겠습니까?')) return;

    deletingId.value = id;
    try {
        await store.deleteStockRecommendation(id);
        showSuccessSnackbar.value = true;
        snackbarMessage.value = '추천 상품이 삭제되었습니다.';
    } catch (err) {
        console.error('추천 상품 삭제 실패:', err);
        showSuccessSnackbar.value = true;
        snackbarMessage.value = '추천 상품 삭제에 실패했습니다.';
    } finally {
        deletingId.value = null;
    }
}

// 시장별 아이콘 반환
const getMarketIcon = (market) => {
    switch (market) {
        case 'KOSPI':
            return 'mdi-chart-line';
        case 'KOSDAQ':
            return 'mdi-chart-bar';
        case 'KONEX':
            return 'mdi-chart-bubble';
        default:
            return 'mdi-chart-line';
    }
}

// 시장별 색상 반환
const getMarketColor = (market) => {
    switch (market) {
        case 'KOSPI':
            return 'primary';
        case 'KOSDAQ':
            return 'secondary';
        case 'KONEX':
            return 'info';
        default:
            return 'grey';
    }
}

onMounted(async () => {
    if (!auth.token) {
        router.push('/login');
        return;
    }

    try {
        // 추천 데이터 로드
        await refreshRecommendations();
        // 저장된 추천 상품 로드
        await store.fetchSavedRecommendations();
    } catch (error) {
        console.error('데이터 로드 실패:', error);
        if (error.response?.status === 401) {
            auth.clearAuth();
            router.push('/login');
        }
    }
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

.bg-success {
    background-color: #4CAF50 !important;
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

/* 버튼 간격 */
.gap-2 {
    gap: 8px;
}

/* 버튼 호버 효과 */
.v-btn {
    transition: all 0.2s ease;
}

.v-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 저장된 추천 상품 스타일 */
.saved-item {
    transition: all 0.2s ease;
    border-radius: 8px;
    margin-bottom: 8px;
    padding: 8px;
    position: relative;
}

.saved-item:hover {
    background-color: rgba(0, 0, 0, 0.04);
}

.delete-btn {
    opacity: 0.8;
    transition: all 0.2s ease;
    min-width: 36px !important;
    width: 36px !important;
    height: 36px !important;
    color: rgb(var(--v-theme-error)) !important;
}

.delete-btn:hover {
    opacity: 1;
    transform: scale(1.1);
    background-color: rgba(var(--v-theme-error), 0.1) !important;
}

.delete-btn .v-icon {
    font-size: 20px;
    color: rgb(var(--v-theme-error)) !important;
}

/* 전체 삭제 버튼 호버 효과 */
.v-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 추천 버튼 스타일 */
.recommend-btn {
    min-width: 200px;
    height: 48px;
    font-size: 1.1rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
}

.recommend-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.recommend-btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(25, 118, 210, 0.2);
}

/* 반응형 디자인 */
@media (max-width: 600px) {
    .recommend-btn {
        min-width: 160px;
        height: 44px;
        font-size: 1rem;
    }
}
</style>