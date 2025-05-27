<template>
    <v-list-item class="recommendation-item">
        <template v-slot:prepend>
            <v-avatar :color="getTypeColor(item.type)" class="mr-3">
                <v-icon color="white">{{ getTypeIcon(item.type) }}</v-icon>
            </v-avatar>
        </template>
        
        <v-list-item-title class="d-flex align-center font-weight-bold">
            {{ item.name }}
            <v-chip
                class="ml-2"
                :color="getTypeColor(item.type)"
                size="small"
            >
                {{ item.type }}
            </v-chip>
        </v-list-item-title>
        
        <v-list-item-subtitle class="mt-2">
            <div class="d-flex align-center">
                <span class="text-body-2">{{ item.bank || '제공기관 정보 없음' }}</span>
                <v-chip v-if="item.market" size="x-small" class="ml-2" color="grey-lighten-3">
                    {{ item.market }}
                </v-chip>
                <v-chip v-if="item.sector" size="x-small" class="ml-2" color="grey-lighten-3">
                    {{ item.sector }}
                </v-chip>
            </div>
            
            <div class="mt-2">
                <template v-if="item.options && item.options.length > 0">
                    <v-chip color="success" size="small" class="mr-2">
                        최고 수익률: {{ Math.max(...item.options.map(opt => opt.intr_rate2)) }}%
                    </v-chip>
                    <v-chip color="info" size="small">
                        가입기간: {{ item.options.map(opt => opt.save_trm).join(', ') }}개월
                    </v-chip>
                </template>
                <template v-else-if="item.return_rate">
                    <v-chip color="success" size="small">
                        수익률: {{ item.return_rate }}%
                    </v-chip>
                </template>
            </div>
        </v-list-item-subtitle>
        
        <template v-slot:append>
            <v-btn 
                v-if="item.type === '주식'" 
                color="primary" 
                variant="tonal" 
                size="small"
                @click="$emit('save-stock', item)"
            >
                <v-icon size="small" class="mr-1">mdi-bookmark-plus</v-icon>
                저장
            </v-btn>
        </template>
    </v-list-item>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

defineEmits(['save-stock']);

const props = defineProps({
    item: {
        type: Object,
        required: true
    }
});

function getTypeColor(type) {
    const colors = {
        '예금': 'blue',
        '적금': 'green',
        '주식': 'purple',
        'ETF': 'amber',
        '펀드': 'deep-purple'
    };
    return colors[type] || 'grey';
}

function getTypeIcon(type) {
    const icons = {
        '예금': 'mdi-bank',
        '적금': 'mdi-piggy-bank',
        '주식': 'mdi-chart-line',
        'ETF': 'mdi-chart-box',
        '펀드': 'mdi-chart-pie'
    };
    return icons[type] || 'mdi-help-circle';
}
</script>

<style scoped>
.recommendation-item {
    border-radius: 8px;
    margin-bottom: 8px;
    transition: all 0.2s ease;
}

.recommendation-item:hover {
    background-color: rgba(0, 0, 0, 0.03);
}

.v-list-item-title {
    font-weight: 500;
}

.v-chip {
    font-size: 0.75rem;
}
</style>