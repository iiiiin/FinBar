<template>
    <div class="survey-page">
        <NavigationBar />
        
        <!-- 고정된 진행 상태 바 -->
        <div class="progress-bar-container">
            <v-container>
                <v-row justify="center" align="center" class="py-2">
                    <v-col cols="12" md="8" lg="6">
                        <div class="d-flex align-center justify-space-between mb-1">
                            <span class="text-caption">진행률: {{ Math.round(progressPercentage) }}%</span>
                            <span class="text-caption">{{ currentQuestionIndex + 1 }} / {{ questions.length }} 문항</span>
                        </div>
                        <v-progress-linear
                            :model-value="progressPercentage"
                            color="primary"
                            height="8"
                            rounded
                        />
                    </v-col>
                </v-row>
            </v-container>
        </div>

        <v-main>
            <v-container class="py-8">
                <!-- 헤더 섹션 -->
                <v-row justify="center" class="mb-6">
                    <v-col cols="12" md="8" lg="6">
                        <div class="text-center">
                            <h1 class="text-h3 font-weight-bold mb-2">투자 성향 분석</h1>
                            <p class="text-subtitle-1 text-grey-darken-1">
                                간단한 설문을 통해 나에게 맞는 투자 성향을 파악해보세요
                            </p>
                        </div>
                    </v-col>
                </v-row>

                <!-- 메인 컨텐츠 -->
                <v-row justify="center">
                    <v-col cols="12" md="8" lg="6">
                        <v-card elevation="3" class="rounded-lg">
                            <!-- 로딩 상태 -->
                            <v-card-text v-if="loading" class="text-center py-8">
                                <v-progress-circular indeterminate color="primary" size="64" />
                                <p class="mt-4 text-subtitle-1">설문 문항을 불러오는 중...</p>
                            </v-card-text>

                            <!-- 에러 상태 -->
                            <v-card-text v-else-if="error" class="pa-6">
                                <v-alert type="error" variant="tonal">
                                    <v-alert-title>오류 발생</v-alert-title>
                                    {{ error.message || '에러가 발생했습니다.' }}
                                </v-alert>
                                <div class="text-center mt-4">
                                    <v-btn 
                                        color="primary" 
                                        variant="outlined"
                                        @click="retryFetch"
                                    >
                                        다시 시도
                                    </v-btn>
                                </div>
                            </v-card-text>

                            <!-- 현재 설문 문항 -->
                            <template v-else-if="!loading && !error && questions.length > 0">
                                <v-card-title class="text-h5 py-4 px-6 bg-primary text-white">
                                    <v-icon class="mr-3">mdi-clipboard-check</v-icon>
                                    투자 성향 설문조사
                                </v-card-title>

                                <v-card-text class="pa-6">
                                    <div v-if="currentQuestion" class="question-container">
                                        <SurveyQuestionItem 
                                            :question="currentQuestion"
                                            :selectedChoice="answers[currentQuestion.id]"
                                            @select="choiceId => handleAnswer(currentQuestion.id, choiceId)"
                                        />
                                    </div>
                                </v-card-text>

                                <!-- 네비게이션 버튼 -->
                                <v-card-actions class="justify-center pa-6 bg-grey-lighten-5 button-container">
                                    <div class="d-flex justify-center gap-4">
                                        <v-btn
                                            color="grey"
                                            variant="outlined"
                                            @click="previousQuestion"
                                            :disabled="currentQuestionIndex === 0"
                                        >
                                            이전
                                        </v-btn>
                                        
                                        <v-btn
                                            v-if="currentQuestionIndex < questions.length - 1"
                                            color="primary"
                                            variant="elevated"
                                            @click="nextQuestion"
                                            :disabled="!answers[currentQuestion?.id]"
                                        >
                                            다음
                                        </v-btn>
                                        
                                        <v-btn
                                            v-else
                                            color="success"
                                            variant="elevated"
                                            @click="onSubmit"
                                            :loading="submitting"
                                            :disabled="!isValidForm"
                                        >
                                            제출하기
                                        </v-btn>
                                    </div>
                                </v-card-actions>
                            </template>

                            <!-- 빈 상태 -->
                            <v-card-text v-else class="text-center py-8">
                                <v-icon size="64" color="grey-lighten-1">mdi-alert-circle-outline</v-icon>
                                <p class="mt-4 text-subtitle-1">설문 문항이 없습니다.</p>
                            </v-card-text>
                        </v-card>

                        <!-- 설문 안내사항 -->
                        <v-card variant="outlined" class="mt-6">
                            <v-card-text>
                                <h3 class="text-h6 mb-3">
                                    <v-icon class="mr-2">mdi-information-outline</v-icon>
                                    설문 안내
                                </h3>
                                <v-list density="compact">
                                    <v-list-item>
                                        <template v-slot:prepend>
                                            <v-icon size="small" color="primary">mdi-check</v-icon>
                                        </template>
                                        <v-list-item-title>솔직하게 답변해주세요</v-list-item-title>
                                        <v-list-item-subtitle>정확한 투자 성향 분석을 위해 본인의 생각을 그대로 표현해주세요</v-list-item-subtitle>
                                    </v-list-item>
                                    <v-list-item>
                                        <template v-slot:prepend>
                                            <v-icon size="small" color="primary">mdi-check</v-icon>
                                        </template>
                                        <v-list-item-title>모든 문항에 답변해주세요</v-list-item-title>
                                        <v-list-item-subtitle>정확한 분석을 위해 모든 문항에 답변이 필요합니다</v-list-item-subtitle>
                                    </v-list-item>
                                    <v-list-item>
                                        <template v-slot:prepend>
                                            <v-icon size="small" color="primary">mdi-check</v-icon>
                                        </template>
                                        <v-list-item-title>약 5분 정도 소요됩니다</v-list-item-title>
                                        <v-list-item-subtitle>차분히 생각하며 답변해주세요</v-list-item-subtitle>
                                    </v-list-item>
                                </v-list>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-main>

        <!-- 결과 다이얼로그 -->
        <v-dialog v-model="showResultDialog" max-width="500" persistent>
            <v-card>
                <v-card-title class="text-h5 pa-4 bg-success text-white">
                    <v-icon class="mr-2">mdi-check-circle</v-icon>
                    분석 완료!
                </v-card-title>
                
                <v-card-text class="pa-6 text-center">
                    <v-icon size="64" color="success" class="mb-4">mdi-account-check</v-icon>
                    <h3 class="text-h4 mb-2">{{ resultData.risk_type }}</h3>
                    <p class="text-subtitle-1 text-grey-darken-1">
                        총점: {{ resultData.total_score }}점
                    </p>
                    <v-divider class="my-4" />
                    <p class="text-body-2">
                        투자 성향 분석이 완료되었습니다.<br>
                        이제 투자 목표를 설정하고 맞춤 상품을 추천받아보세요!
                    </p>
                </v-card-text>
                
                <v-card-actions class="justify-center pa-4">
                    <v-btn 
                        color="primary" 
                        variant="elevated"
                        @click="goToProfile"
                    >
                        투자 프로필로 이동
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useSurveyStore } from '@/stores/surveyStore';
import { useRouter } from 'vue-router';
import SurveyQuestionItem from '@/components/SurveyQuestionItem.vue';
import NavigationBar from '@/components/NavigationBar.vue';
import { surveyAPI } from '@/services/api';
import { investmentAPI } from '@/services/api';

const router = useRouter();
const store = useSurveyStore();

// store에서 상태 가져오기
const questions = computed(() => {
    console.log('현재 질문 데이터:', store.questions);
    return store.questions;
});
const answers = computed(() => store.answers);
const loading = computed(() => store.loading);
const error = computed(() => store.error);

// 상태 관리
const submitting = ref(false);
const showResultDialog = ref(false);
const currentQuestionIndex = ref(0);
const resultData = ref({
    risk_type: '',
    total_score: 0
});

// 현재 질문
const currentQuestion = computed(() => {
    if (!questions.value || questions.value.length === 0) return null;
    return questions.value[currentQuestionIndex.value];
});

// Computed
const isValidForm = computed(() => {
    return questions.value.length > 0 && 
           Object.keys(answers.value).length === questions.value.length;
});

const progressPercentage = computed(() => {
    if (questions.value.length === 0) return 0;
    return (Object.keys(answers.value).length / questions.value.length) * 100;
});

// Methods
function handleAnswer(questionId, choiceId) {
    console.log(`답변 저장: 질문 ${questionId}, 선택 ${choiceId}`);
    store.setAnswer(questionId, choiceId);
    if (currentQuestionIndex.value < questions.value.length - 1) {
        setTimeout(() => {
            nextQuestion();
        }, 500);
    }
}

function nextQuestion() {
    if (currentQuestionIndex.value < questions.value.length - 1) {
        currentQuestionIndex.value++;
    }
}

function previousQuestion() {
    if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--;
    }
}

async function onSubmit() {
    if (!isValidForm.value) {
        alert('모든 문항에 답변해주세요.');
        return;
    }
    
    submitting.value = true;
    try {
        // 현재 선택된 답변들을 백엔드가 기대하는 형식으로 변환
        const formattedAnswers = Object.entries(answers.value).map(([questionId, choiceId]) => ({
            question_id: parseInt(questionId),
            choice_id: choiceId
        }));

        const response = await surveyAPI.submitAnswers({ answers: formattedAnswers });
        resultData.value = {
            risk_type: response.data.risk_type,
            total_score: response.data.total_score
        };

        try {
            await investmentAPI.getRiskProfile();
            await investmentAPI.updateRiskProfile({
                total_score: resultData.value.total_score,
                risk_type: resultData.value.risk_type
            });
        } catch (e) {
            if (e.response?.status === 404) {
                await investmentAPI.createRiskProfile({
                    total_score: resultData.value.total_score,
                    risk_type: resultData.value.risk_type
                });
            }
        }

        showResultDialog.value = true;
    } catch (err) {
        console.error('Submit error:', err);
        if (err.response?.status === 401) {
            alert('로그인이 필요합니다.');
            router.push('/login');
        } else {
            alert(err.response?.data?.error || '제출 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
    } finally {
        submitting.value = false;
    }
}

async function retryFetch() {
    try {
        console.log('설문 데이터 재요청 시작');
        await store.fetchQuestions();
    } catch (err) {
        console.error('Failed to fetch questions:', err);
        if (err.response?.status === 401) {
            alert('로그인이 필요합니다.');
            router.push('/login');
        } else if (err.response?.status === 500) {
            alert('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
        } else {
            alert(err.message || '설문 데이터를 불러오는데 실패했습니다.');
        }
    }
}

function goToProfile() {
    router.push('/investment-profile');
}

// Lifecycle
onMounted(async () => {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('토큰이 없습니다.');
            alert('로그인이 필요합니다.');
            router.push('/login');
            return;
        }

        console.log('컴포넌트 마운트 - 설문 데이터 요청 시작');
        await store.fetchQuestions();
    } catch (err) {
        console.error('Error in component mount:', err);
        if (err.response?.status === 401) {
            console.error('인증 오류:', err.response.data);
            alert('로그인이 필요합니다.');
            router.push('/login');
        } else if (err.response?.status === 500) {
            console.error('서버 오류:', err.response.data);
            alert('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
        } else {
            console.error('기타 오류:', err);
            alert(err.message || '설문 데이터를 불러오는데 실패했습니다.');
        }
    }
});
</script>

<style scoped>
.survey-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background-color: #f5f5f5;
}

.progress-bar-container {
    position: sticky;
    top: 64px; /* NavigationBar 높이 */
    background-color: white;
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.v-main {
    flex: 1;
    padding-top: 64px; /* NavBar 높이만큼 상단 패딩 추가 */
}

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

/* 프로그레스 바 애니메이션 */
.v-progress-linear {
    transition: all 0.3s ease;
}

/* 카드 호버 효과 */
.v-card {
    transition: transform 0.2s ease;
}

.v-card:hover {
    transform: translateY(-2px);
}

/* 반응형 디자인 */
@media (max-width: 600px) {
    .text-h3 {
        font-size: 1.75rem !important;
    }
    
    .v-container {
        padding: 16px !important;
    }
}

.question-container {
    min-height: 200px;
}

/* 버튼 컨테이너 스타일 */
.button-container {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.gap-4 {
    gap: 1rem;
}

/* 버튼 스타일 */
.v-btn {
    min-width: 100px;
}
</style>