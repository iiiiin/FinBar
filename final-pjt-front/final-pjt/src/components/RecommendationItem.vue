<template>
    <v-list-item>
        <v-list-item-content>
            <v-list-item-title class="d-flex align-center">
                {{ item.name }}
                <v-chip
                    class="ml-2"
                    :color="getTypeColor(item.type)"
                    size="small"
                >
                    {{ item.type }}
                </v-chip>
            </v-list-item-title>
            <v-list-item-subtitle>
                <div>{{ item.bank }}</div>
                <div v-if="item.options && item.options.length > 0">
                    <strong>최고 수익률:</strong> {{ Math.max(...item.options.map(opt => opt.intr_rate2)) }}%
                    <br>
                    <strong>가입기간:</strong> {{ item.options.map(opt => opt.save_trm).join(', ') }}개월
                </div>
                <div v-else-if="item.return_rate">
                    <strong>수익률:</strong> {{ item.return_rate }}%
                </div>
            </v-list-item-subtitle>
        </v-list-item-content>
    </v-list-item>
</template>

<script setup>
import { defineProps } from 'vue';

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
        '주식': 'purple'
    };
    return colors[type] || 'grey';
}
</script>

<style scoped>
.v-list-item-title {
    font-weight: 500;
}

.v-chip {
    font-size: 0.75rem;
}
</style>