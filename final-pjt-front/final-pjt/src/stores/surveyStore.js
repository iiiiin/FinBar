import { defineStore } from 'pinia';
import apiClient from '@/services/api';

export const useSurveyStore = defineStore('survey', {
    state: () => ({
        questions: [],        // API에서 가져온 설문 문항
        answers: {},          // { [questionId]: choiceId }
        loading: false,
        error: null,
    }),
    getters: {
        getQuestions: (state) => state.questions,
        getAnswers: (state) => state.answers,
        isLoading: (state) => state.loading,
        getError: (state) => state.error,
        // 답변 완료된 질문 수
        answeredCount: (state) => Object.keys(state.answers).length,
        // 전체 질문 수
        totalQuestions: (state) => state.questions.length,
        // 진행률
        progressPercentage: (state) => {
            if (state.questions.length === 0) return 0;
            return (Object.keys(state.answers).length / state.questions.length) * 100;
        }
    },
    actions: {
        // 인증 헤더 생성
        authHeader() {
            const token = localStorage.getItem('token');
            return token ? { Authorization: `Token ${token}` } : {};
        },

        // 문항 가져오기
        async fetchQuestions() {
            this.loading = true;
            this.error = null;
            try {
                const response = await apiClient.getQuestions();
                console.log('받은 설문 데이터:', response.data);
                if (!Array.isArray(response.data)) {
                    throw new Error('Invalid response format');
                }
                this.questions = response.data;
                return response.data;
            } catch (err) {
                console.error('설문 데이터 가져오기 실패:', err);
                this.error = err;
                throw err;
            } finally {
                this.loading = false;
            }
        },

        // 선택 값 저장
        setAnswer(questionId, choiceId) {
            if (!questionId || !choiceId) {
                console.warn('Invalid answer data:', { questionId, choiceId });
                return;
            }
            console.log(`답변 저장: 질문 ${questionId}, 선택 ${choiceId}`);
            this.answers = { ...this.answers, [questionId]: choiceId };
            console.log('현재 저장된 답변들:', this.answers);
        },

        // 답안 제출
        async submitAnswers() {
            if (Object.keys(this.answers).length === 0) {
                throw new Error('No answers to submit');
            }

            this.loading = true;
            try {
                // 백엔드 요구사항에 맞게 데이터 형식 변환
                const formattedAnswers = Object.entries(this.answers).map(([questionId, choiceId]) => ({
                    question_id: parseInt(questionId),
                    choice_id: choiceId
                }));

                console.log('제출할 답변 데이터:', { answers: formattedAnswers });
                const response = await apiClient.submitAnswers({
                    answers: formattedAnswers
                });
                console.log('제출 응답:', response.data);

                return response;
            } catch (err) {
                console.error('답변 제출 실패:', err);
                throw err;
            } finally {
                this.loading = false;
            }
        },

        // 상태 초기화
        clearAnswers() {
            this.answers = {};
            console.log('답변 초기화 완료');
        },

        resetState() {
            this.questions = [];
            this.answers = {};
            this.loading = false;
            this.error = null;
        }
    }
}, {
    strict: false
});