<template>
    <v-list two-line>
        <template v-if="loading">
            <v-list-item>
                <v-list-item-content>로딩 중...</v-list-item-content>
            </v-list-item>
        </template>
        <template v-else-if="error">
            <v-list-item>
                <v-list-item-content>에러 발생: {{ error.message }}</v-list-item-content>
            </v-list-item>
        </template>
        <template v-else-if="!items || items.length === 0">
            <v-list-item>
                <v-list-item-content>
                    <v-list-item-title>추천 상품이 없습니다.</v-list-item-title>
                    <v-list-item-subtitle>다른 필터 조건을 시도해보세요.</v-list-item-subtitle>
                </v-list-item-content>
            </v-list-item>
        </template>
        <template v-else>
            <RecommendationItem 
                v-for="item in items" 
                :key="item.product_code || item.id" 
                :item="item" 
                @save-stock="$emit('save-stock', $event)"
            />
        </template>
    </v-list>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import RecommendationItem from '@/components/RecommendationItem.vue';

defineEmits(['save-stock']);

const props = defineProps({
    items: Array,
    loading: Boolean,
    error: Object,
});
</script>