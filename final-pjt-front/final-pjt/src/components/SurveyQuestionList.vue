<!-- src/components/SurveyQuestionList.vue -->
<template>
    <v-form>
        <div v-for="question in questions" :key="question.id">
            <SurveyQuestionItem :question="question" :selectedChoice="answers[question.id] || null"
                @select="choiceId => $emit('update-answer', question.id, choiceId)" />
        </div>
    </v-form>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import SurveyQuestionItem from '@/components/SurveyQuestionItem.vue';

const props = defineProps({
    questions: { type: Array, required: true },
    answers: { type: Object, required: true },
});
const emit = defineEmits(['update-answer']);
</script>