<!-- src/components/SurveyQuestionItem.vue -->
<template>
    <div class="survey-question-item">
        <!-- 디버깅용 정보 -->
        <div v-if="false" class="debug-info">
            <pre>{{ JSON.stringify(question, null, 2) }}</pre>
        </div>

        <v-card flat class="survey-question-card">
            <v-card-text class="pa-4">
                <div class="text-subtitle-1 font-weight-medium mb-4">
                    {{ question.question_text }}
                </div>
                <v-radio-group 
                    v-model="localChoice"
                    @update:model-value="handleChange"
                    class="choice-group"
                >
                    <v-radio
                        v-for="choice in question.choices"
                        :key="choice.id"
                        :value="choice.id"
                        :label="choice.choice_text"
                        color="primary"
                        class="choice-radio"
                    />
                </v-radio-group>
            </v-card-text>
        </v-card>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
    question: {
        type: Object,
        required: true,
        validator: (prop) => {
            const isValid = prop.id && prop.question_text && Array.isArray(prop.choices);
            if (!isValid) {
                console.warn('Invalid question prop:', prop);
            }
            return isValid;
        }
    },
    selectedChoice: {
        type: Number,
        default: null
    }
});

const emit = defineEmits(['select']);

// 로컬 상태 관리
const localChoice = ref(props.selectedChoice);

// props 변경 감지
watch(() => props.selectedChoice, (newVal) => {
    console.log('선택지 변경:', newVal);  // 디버깅용 로그
    if (newVal !== localChoice.value) {
        localChoice.value = newVal;
    }
});

// 선택 변경 처리
function handleChange(value) {
    console.log('선택된 값:', value);  // 디버깅용 로그
    emit('select', value);
}

// 컴포넌트 마운트 시 초기값 설정
onMounted(() => {
    console.log('질문 데이터:', props.question);  // 디버깅용 로그
    localChoice.value = props.selectedChoice;
});
</script>

<style scoped>
.survey-question-item {
    width: 100%;
}

.survey-question-card {
    background: transparent;
}

.choice-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.choice-radio {
    margin: 0;
    padding: 12px;
    border-radius: 8px;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}

.choice-radio:hover {
    background-color: rgba(25, 118, 210, 0.04);
    border-color: rgba(25, 118, 210, 0.1);
}

/* 디버깅 정보 스타일 */
.debug-info {
    background: #f5f5f5;
    padding: 8px;
    margin-bottom: 8px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 12px;
}

/* 라디오 버튼 스타일링 */
:deep(.v-radio) {
    margin-top: 0;
}

:deep(.v-radio .v-label) {
    font-size: 1rem;
    line-height: 1.5;
}

:deep(.v-radio--selected) {
    background-color: rgba(25, 118, 210, 0.08);
    border-radius: 8px;
}

/* 선택지 호버 효과 */
:deep(.v-radio:hover) {
    background-color: rgba(25, 118, 210, 0.04);
    border-radius: 8px;
}
</style>