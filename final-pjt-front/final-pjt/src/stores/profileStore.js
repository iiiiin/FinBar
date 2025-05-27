import { defineStore } from 'pinia'
import { investmentAPI } from '@/services/api'

// 캐시 유효 시간 (5분)
const CACHE_DURATION = 5 * 60 * 1000

export const useProfileStore = defineStore('profile', {
    state: () => ({
        profile: null,
        goal: null,
        loading: false,
        error: null,
        // 캐시 관련 상태
        cache: {
            profile: null,
            goal: null,
            lastFetched: null
        }
    }),

    getters: {
        getProfile: (state) => state.profile,
        getGoal: (state) => state.goal,
        isLoading: (state) => state.loading,
        getError: (state) => state.error,

        // 캐시 유효성 검사
        isCacheValid: (state) => {
            if (!state.cache.lastFetched) return false
            return Date.now() - state.cache.lastFetched < CACHE_DURATION
        },

        // 프로필 요약 정보
        profileSummary: (state) => {
            if (!state.profile || !state.goal) return null

            return {
                risk_type: state.profile.risk_type,
                required_return: state.goal.required_return,
                preferred_period: state.goal.preferred_period,
                target_amount: state.goal.target_amount,
                current_amount: state.goal.current_amount,
                target_date: state.goal.target_date
            }
        }
    },

    actions: {
        // 프로필 데이터 가져오기 (캐시 적용)
        async fetchProfile() {
            // 캐시가 유효한 경우 캐시된 데이터 반환
            if (this.isCacheValid && this.cache.profile) {
                console.log('캐시된 프로필 데이터 사용')
                this.profile = this.cache.profile
                this.goal = this.cache.goal
                return
            }

            this.loading = true
            this.error = null

            try {
                const response = await investmentAPI.getProfile()
                const data = response.data

                // 상태 업데이트
                this.profile = {
                    risk_type: data.risk_type,
                    total_score: data.total_score,
                    evaluated_at: data.evaluated_at
                }
                this.goal = data.goal

                // 캐시 업데이트
                this.cache.profile = this.profile
                this.cache.goal = this.goal
                this.cache.lastFetched = Date.now()

            } catch (err) {
                this.error = err
                throw err
            } finally {
                this.loading = false
            }
        },

        // 캐시 무효화
        invalidateCache() {
            this.cache.profile = null
            this.cache.goal = null
            this.cache.lastFetched = null
        },

        // 상태 초기화
        clearState() {
            this.profile = null
            this.goal = null
            this.loading = false
            this.error = null
            this.invalidateCache()
        }
    }
}) 