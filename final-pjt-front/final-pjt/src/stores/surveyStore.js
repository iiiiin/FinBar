import { defineStore } from 'pinia';
import { surveyAPI } from '@/services/api';

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
        getAuthHeader() {
            const token = localStorage.getItem('token');
            return token ? { Authorization: `Token ${token}` } : {};
        },

        // 문항 가져오기
        async fetchQuestions() {
            this.loading = true;
            this.error = null;
            try {
                console.log('설문 데이터 요청 시작');
                const token = localStorage.getItem('token');
                if (!token) {
                    throw new Error('인증 토큰이 없습니다.');
                }

                const response = await surveyAPI.getQuestions(this.getAuthHeader());

                console.log('설문 데이터 응답:', response);

                if (!response?.data) {
                    throw new Error('응답 데이터가 없습니다.');
                }

                if (!Array.isArray(response.data)) {
                    console.error('잘못된 응답 형식:', response.data);
                    throw new Error('서버 응답 형식이 올바르지 않습니다.');
                }

                this.questions = response.data;
                console.log('설문 데이터 저장 완료:', this.questions);
                return response.data;
            } catch (err) {
                console.error('설문 데이터 가져오기 실패:', err);
                if (err.response) {
                    console.error('서버 응답:', err.response.data);
                    console.error('상태 코드:', err.response.status);
                }
                this.error = err.response?.data?.message || err.message || '설문 데이터를 가져오는데 실패했습니다.';
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
                const response = await surveyAPI.submitAnswers(formattedAnswers, this.getAuthHeader());
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