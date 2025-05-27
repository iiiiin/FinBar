// src/stores/recommendationStore.js
import { defineStore } from 'pinia';
import { recommendationAPI } from '@/services/api';

// 캐시 유효 시간 (5분)
const CACHE_DURATION = 5 * 60 * 1000;

export const useRecommendationStore = defineStore('recommendation', {
    state: () => ({
        items: [],                 // 추천 상품 목록
        loading: false,            // 로딩 상태
        error: null,               // 에러 상태
        recommendationType: null,   // 추천 유형 (예금, 적금, 주식 등)
        requiredReturn: null,      // 목표 수익률
        factors: null,             // 추천 요인 (위험 성향, 선호 기간 등)
        filters: {                 // 필터 상태
            market: null,          // 시장 필터 (KOSPI, KOSDAQ 등)
            sector: null,          // 섹터 필터 (반도체, 바이오 등)
            category: null         // 카테고리 필터 (예금, 적금 등)
        },
        savedRecommendations: [],   // 저장된 추천 상품
        // 캐시 관련 상태
        cache: {
            recommendations: null,
            lastFetched: null,
            profile: null
        },
        recommendationSummary: null
    }),

    getters: {
        getItems: (state) => state.items,
        isLoading: (state) => state.loading,
        getError: (state) => state.error,
        getRecommendationType: (state) => state.recommendationType,
        getRequiredReturn: (state) => state.requiredReturn,
        getFactors: (state) => state.factors,
        getFilters: (state) => state.filters,

        // 필터링된 아이템 반환
        filteredItems: (state) => {
            if (!state.items.length) return [];

            return state.items.filter(item => {
                // 시장 필터 적용
                if (state.filters.market && item.market &&
                    item.market !== state.filters.market) {
                    return false;
                }

                // 섹터 필터 적용
                if (state.filters.sector && item.sector &&
                    item.sector !== state.filters.sector) {
                    return false;
                }

                // 카테고리 필터 적용
                if (state.filters.category && item.type &&
                    item.type !== state.filters.category) {
                    return false;
                }

                return true;
            });
        },

        // 추천 요약 정보
        recommendationSummary: (state) => {
            return {
                risk_type: state.factors?.by_risk || '',
                required_return: state.requiredReturn || 0,
                preferred_period: state.factors?.preferred_period || 0
            };
        },

        // 저장된 추천 상품 수
        savedCount: (state) => state.savedRecommendations.length,

        // 캐시 유효성 검사
        isCacheValid: (state) => {
            if (!state.cache.lastFetched) return false;
            return Date.now() - state.cache.lastFetched < CACHE_DURATION;
        }
    },

    actions: {
        // 필터 설정
        setFilter(filterType, value) {
            this.filters[filterType] = value;
        },

        // 모든 필터 초기화
        clearFilters() {
            this.filters = {
                market: null,
                sector: null,
                category: null
            };
        },

        // 추천 데이터 가져오기 (캐시 적용)
        async fetchRecommendations(params = {}) {
            // 캐시가 유효한 경우 캐시된 데이터 반환
            if (this.isCacheValid && this.cache.recommendations) {
                console.log('캐시된 추천 데이터 사용');
                return this.cache.recommendations;
            }

            this.loading = true;
            this.error = null;

            try {
                const queryParams = {
                    ...params,
                    market: params.market || this.filters.market,
                    sector: params.sector || this.filters.sector,
                    category: params.category || this.filters.category
                };

                const response = await recommendationAPI.getByGoal(queryParams);
                const data = response.data;

                // 상태 업데이트
                this.items = data.items || [];
                this.recommendationType = data.recommendation_type;
                this.requiredReturn = data.required_return;
                this.factors = data.factors;

                // 캐시 업데이트
                this.cache.recommendations = data;
                this.cache.lastFetched = Date.now();

                return data;
            } catch (err) {
                this.error = err;
                throw err;
            } finally {
                this.loading = false;
            }
        },

        // 주식 추천 저장
        async saveStockRecommendations(stocks) {
            try {
                const response = await recommendationAPI.saveStocks(stocks);
                // 저장된 추천 목록 업데이트
                this.savedRecommendations = [...this.savedRecommendations, ...stocks];
                return response;
            } catch (err) {
                this.error = err;
                throw err;
            }
        },

        // 저장된 추천 상품 가져오기 (캐시 적용)
        async fetchSavedRecommendations() {
            if (this.isCacheValid && this.cache.savedRecommendations) {
                console.log('캐시된 저장된 추천 데이터 사용');
                return this.cache.savedRecommendations;
            }

            try {
                const response = await recommendationAPI.getSavedRecommendations();
                const data = response.data || [];

                this.savedRecommendations = data;
                this.cache.savedRecommendations = data;
                this.cache.lastFetched = Date.now();

                return data;
            } catch (err) {
                console.error('저장된 추천 상품 조회 실패:', err);
                return [];
            }
        },

        // 캐시 무효화
        invalidateCache() {
            this.cache.recommendations = null;
            this.cache.savedRecommendations = null;
            this.cache.lastFetched = null;
        },

        // 상태 초기화 (캐시 포함)
        clearState() {
            this.items = [];
            this.loading = false;
            this.error = null;
            this.recommendationType = null;
            this.requiredReturn = null;
            this.factors = null;
            this.filters = {
                market: null,
                sector: null,
                category: null
            };
            this.invalidateCache();
            this.recommendationSummary = null;
        },

        // 개별 추천 상품 삭제
        async deleteStockRecommendation(id) {
            try {
                await recommendationAPI.deleteSavedRecommendation(id);
                // 로컬 상태 업데이트
                this.savedRecommendations = this.savedRecommendations.filter(item => item.id !== id);
                // 캐시 무효화
                this.invalidateCache();
                return true;
            } catch (error) {
                console.error('추천 상품 삭제 실패:', error);
                throw error;
            }
        },

        // 전체 추천 상품 삭제
        async deleteAllSavedRecommendations() {
            try {
                await recommendationAPI.deleteAllSavedRecommendations();
                // 로컬 상태 초기화
                this.savedRecommendations = [];
                // 캐시 무효화
                this.invalidateCache();
                return true;
            } catch (error) {
                console.error('전체 삭제 실패:', error);
                throw error;
            }
        },
    }
}, {
    strict: false
});