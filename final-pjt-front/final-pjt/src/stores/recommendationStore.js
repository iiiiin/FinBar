// src/stores/recommendationStore.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api';

// 상수 정의
const CACHE_DURATION = 5 * 60 * 1000; // 5분
const DEFAULT_FILTERS = {
    market: null,
    sector: null,
    category: null
};

const DEFAULT_RECOMMENDATION_SUMMARY = {
    risk_type: '',
    required_return: 0,
    preferred_period: 0
};

export const useRecommendationStore = defineStore('recommendation', {
    state: () => ({
        items: [],
        loading: false,
        error: null,
        recommendationType: null,
        requiredReturn: null,
        factors: null,
        filters: { ...DEFAULT_FILTERS },
        savedRecommendations: [],
        cache: {
            recommendations: null,
            lastFetched: null,
            profile: null
        },
        recommendationSummary: { ...DEFAULT_RECOMMENDATION_SUMMARY }
    }),

    getters: {
        getItems: (state) => state.items || [],
        isLoading: (state) => state.loading,
        getError: (state) => state.error,
        getRecommendationType: (state) => state.recommendationType,
        getRequiredReturn: (state) => state.requiredReturn,
        getFactors: (state) => state.factors,
        getFilters: (state) => state.filters,

        filteredItems: (state) => {
            if (!state.items?.length) return [];

            return state.items.filter(item => {
                if (!item) return false;

                const { market, sector, category } = state.filters;

                if (market && item.market && item.market !== market) return false;
                if (sector && item.sector && item.sector !== sector) return false;
                if (category && item.type && item.type !== category) return false;

                return true;
            });
        },

        savedCount: (state) => state.savedRecommendations.length,

        isCacheValid: (state) => {
            if (!state.cache.lastFetched) return false;
            return Date.now() - state.cache.lastFetched < CACHE_DURATION;
        }
    },

    actions: {
        setFilter(filterType, value) {
            if (!(filterType in this.filters)) {
                throw new Error(`유효하지 않은 필터 타입입니다: ${filterType}`);
            }
            this.filters[filterType] = value;
        },

        clearFilters() {
            this.filters = { ...DEFAULT_FILTERS };
        },

        updateRecommendationSummary() {
            this.recommendationSummary = {
                risk_type: this.factors?.by_risk || '',
                required_return: this.requiredReturn || 0,
                preferred_period: this.factors?.preferred_period || 0
            };
        },

        async fetchRecommendations(params = {}) {
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

                const response = await apiClient.getByGoal(queryParams);

                if (!response?.data) {
                    throw new Error('응답 데이터가 올바르지 않습니다.');
                }

                const data = response.data;

                // 상태 업데이트
                this.items = data.items || [];
                this.recommendationType = data.recommendation_type;
                this.requiredReturn = data.required_return;
                this.factors = data.factors;

                // 추천 요약 정보 업데이트
                this.updateRecommendationSummary();

                // 캐시 업데이트
                this.cache.recommendations = data;
                this.cache.lastFetched = Date.now();

                return data;
            } catch (err) {
                this.error = err.response?.data?.message || err.message || '추천 데이터를 가져오는 중 오류가 발생했습니다.';
                throw err;
            } finally {
                this.loading = false;
            }
        },

        async saveStockRecommendations(stocks) {
            if (!Array.isArray(stocks) || stocks.length === 0) {
                throw new Error('저장할 추천 상품이 없습니다.');
            }

            try {
                const response = await apiClient.saveStocks(stocks);

                if (!response?.data) {
                    throw new Error('저장 응답이 올바르지 않습니다.');
                }

                // 저장된 추천 목록 업데이트
                this.savedRecommendations = [...this.savedRecommendations, ...stocks];
                this.invalidateCache(); // 캐시 무효화

                return response.data;
            } catch (err) {
                this.error = err.response?.data?.non_field_errors?.[0] || err.message || '추천 상품 저장 중 오류가 발생했습니다.';
                throw err;
            }
        },

        async fetchSavedRecommendations() {
            if (this.isCacheValid && this.cache.savedRecommendations) {
                console.log('캐시된 저장된 추천 데이터 사용');
                return this.cache.savedRecommendations;
            }

            try {
                const response = await apiClient.getSavedRecommendations();

                if (!response?.data) {
                    throw new Error('저장된 추천 데이터 응답이 올바르지 않습니다.');
                }

                const data = response.data;
                this.savedRecommendations = data;
                this.cache.savedRecommendations = data;
                this.cache.lastFetched = Date.now();

                return data;
            } catch (err) {
                console.error('저장된 추천 상품 조회 실패:', err);
                this.error = err.response?.data?.message || err.message || '저장된 추천 상품을 가져오는 중 오류가 발생했습니다.';
                return [];
            }
        },

        invalidateCache() {
            this.cache.recommendations = null;
            this.cache.savedRecommendations = null;
            this.cache.lastFetched = null;
        },

        clearState() {
            this.items = [];
            this.loading = false;
            this.error = null;
            this.recommendationType = null;
            this.requiredReturn = null;
            this.factors = null;
            this.filters = { ...DEFAULT_FILTERS };
            this.recommendationSummary = { ...DEFAULT_RECOMMENDATION_SUMMARY };
            this.invalidateCache();
        },

        async deleteStockRecommendation(id) {
            if (!id) {
                throw new Error('삭제할 추천 상품 ID가 필요합니다.');
            }

            try {
                await apiClient.deleteStockRecommendation(id);
                this.savedRecommendations = this.savedRecommendations.filter(item => item.id !== id);
                this.invalidateCache();
            } catch (err) {
                this.error = err.response?.data?.message || err.message || '추천 상품 삭제 중 오류가 발생했습니다.';
                throw err;
            }
        },

        async deleteAllSavedRecommendations() {
            try {
                await apiClient.deleteAllSavedRecommendations();
                this.savedRecommendations = [];
                this.invalidateCache();
            } catch (err) {
                this.error = err.response?.data?.message || err.message || '모든 추천 상품 삭제 중 오류가 발생했습니다.';
                throw err;
            }
        }
    }
});