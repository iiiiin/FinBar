// src/stores/recommendationStore.js
import { defineStore } from 'pinia';
import { recommendationAPI } from '@/services/api';

export const useRecommendationStore = defineStore('recommendation', {
    state: () => ({
        items: [],
        loading: false,
        error: null,
        recommendationType: null,
        requiredReturn: null,
        factors: null
    }),
    getters: {
        getItems: (state) => state.items,
        isLoading: (state) => state.loading,
        getError: (state) => state.error,
        getRecommendationType: (state) => state.recommendationType,
        getRequiredReturn: (state) => state.requiredReturn,
        getFactors: (state) => state.factors
    },
    actions: {
        async fetchRecommendations(params = {}) {
            this.loading = true;
            this.error = null;
            try {
                const response = await recommendationAPI.getByGoal(params);
                this.items = response.data.items || [];
                this.recommendationType = response.data.recommendation_type;
                this.requiredReturn = response.data.required_return;
                this.factors = response.data.factors;
                return response.data;
            } catch (err) {
                this.error = err;
                throw err;
            } finally {
                this.loading = false;
            }
        },
        async saveStockRecommendations(stocks) {
            try {
                await recommendationAPI.saveStocks(stocks);
            } catch (err) {
                this.error = err;
                throw err;
            }
        },
        clearState() {
            this.items = [];
            this.loading = false;
            this.error = null;
            this.recommendationType = null;
            this.requiredReturn = null;
            this.factors = null;
        }
    }
}, {
    strict: false
});